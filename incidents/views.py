from datetime import date
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django_otp.decorators import otp_required
from formtools.wizard.views import SessionWizardView

from governanceplatform.helpers import (
    get_active_company_from_session,
    is_user_regulator,
    user_in_group,
)
from governanceplatform.models import Regulation, Regulator, Sector
from governanceplatform.settings import (
    MAX_PRELIMINARY_NOTIFICATION_PER_DAY_PER_USER,
    PUBLIC_URL,
    SITE_NAME,
)

from .decorators import regulator_role_required
from .email import send_email
from .forms import (
    ContactForm,
    ImpactForm,
    QuestionForm,
    RegulationForm,
    RegulatorForm,
    RegulatorIncidentEditForm,
    get_forms_list,
)
from .models import (
    Answer,
    Email,
    Incident,
    IncidentWorkflow,
    PredefinedAnswer,
    Question,
    QuestionCategory,
    SectorRegulation,
)
from .pdf_generation import get_pdf_report


@login_required
@otp_required
def get_incidents(request):
    """Returns the list of incidents depending on the account type."""
    incidents = Incident.objects.order_by("-incident_notification_date")

    if user_in_group(request.user, "RegulatorUser"):
        # RegulatorUser has access to all incidents linked by sectors.
        incidents = incidents.filter(
            affected_services__sector__in=request.user.sectors.all()
        )
    elif user_in_group(request.user, "OperatorAdmin"):
        # OperatorAdmin can see all the reports of the selected company.
        incidents = incidents.filter(company__id=request.session.get("company_in_use"))
    # RegulatorAdmin can see all the incidents reported by operators.
    elif not user_in_group(request.user, "RegulatorAdmin"):
        # OperatorStaff and IncidentUser can see only their reports.
        incidents = incidents.filter(contact_user=request.user)

    if request.GET.get("incidentId"):
        # Search by incident id
        incidents = incidents.filter(
            incident_id__icontains=request.GET.get("incidentId")
        ).distinct()

    # Show 20 incidents per page.
    paginator = Paginator(incidents, 20)
    page_number = request.GET.get("page")
    incidents_page = paginator.get_page(page_number)

    # add paggination to the regular incidents view.
    return render(
        request,
        "regulator/incidents.html"
        if is_user_regulator(request.user)
        else "incidents.html",
        context={
            "site_name": SITE_NAME,
            "incidents": incidents,
            "incidents_page": incidents_page,
        },
    )


@login_required
@otp_required
def get_form_list(request, form_list=None):
    if is_incidents_report_limit_reached(request):
        return HttpResponseRedirect("/incidents")
    """Initialize data for the preliminary notification."""
    if form_list is None:
        form_list = get_forms_list()
    return FormWizardView.as_view(
        form_list,
        initial_dict={"0": ContactForm.prepare_initial_value(request=request)},
        condition_dict={"3": show_sector_form_condition},
    )(request)


@login_required
@otp_required
def get_next_workflow(request, form_list=None, incident_id=None):
    if form_list is None and incident_id is not None:
        incident = Incident.objects.get(id=incident_id)
        form_list = get_forms_list(incident=incident)
    if incident_id is not None:
        request.incident = incident_id
        request.incident_workflow = None
    return WorkflowWizardView.as_view(
        form_list,
    )(request)


@login_required
@otp_required
def edit_workflow(request, form_list=None, incident_workflow_id=None):
    if form_list is None and incident_workflow_id is not None:
        incident_workflow = IncidentWorkflow.objects.get(id=incident_workflow_id)
        form_list = get_forms_list(
            incident=incident_workflow.incident, workflow=incident_workflow.workflow
        )
    if incident_workflow_id is not None:
        request.incident = incident_workflow.incident.id
        request.incident_workflow = incident_workflow.id

    return WorkflowWizardView.as_view(
        form_list,
    )(request)


@login_required
@otp_required
def edit_impacts(request, incident_id=None):
    # OperatorAdmin can access only incidents related to selected company.
    if (
        user_in_group(request.user, "OperatorAdmin")
        and not Incident.objects.filter(
            pk=incident_id, company__id=request.session.get("company_in_use")
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")
    # OperatorStaff and IncidentUser can access only their incidents.
    if (
        not is_user_regulator(request.user)
        and not user_in_group(request.user, "OperatorAdmin")
        and not Incident.objects.filter(
            pk=incident_id, contact_user=request.user
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")

    if incident_id is not None:
        incident = Incident.objects.get(id=incident_id)

    form = ImpactForm(
        incident=incident, data=request.POST if request.method == "POST" else None
    )

    if request.method == "POST":
        if form.is_valid():
            incident.impacts.set(form.cleaned_data["impacts"])
            if len(form.cleaned_data["impacts"]) > 0:
                incident.is_significative_impact = True
            else:
                incident.is_significative_impact = False
            incident.save()
            return HttpResponseRedirect("/incidents")

    return render(request, "edit_impacts.html", {"form": form, "incident": incident})


@login_required
@otp_required
@regulator_role_required
def get_regulator_incident_edit_form(request, incident_id: int):
    """Returns the list of incident as regulator."""
    # RegulatorUser can access only incidents from accessible sectors.
    if (
        user_in_group(request.user, "RegulatorUser")
        and not Incident.objects.filter(
            pk=incident_id, affected_services__sector__in=request.user.sectors.all()
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")

    incident = Incident.objects.get(pk=incident_id)

    regulator_incident_form = RegulatorIncidentEditForm(
        instance=incident, data=request.POST if request.method == "POST" else None
    )
    if request.method == "POST":
        if regulator_incident_form.is_valid():
            regulator_incident_form.save()
            messages.success(
                request,
                f"Incident {incident.incident_id} has been successfully saved.",
            )
            response = HttpResponseRedirect(
                request.session.get("return_page", "/incidents")
            )
            try:
                del request.session["return_page"]
            except KeyError:
                pass

            return response

    if not request.session.get("return_page"):
        request.session["return_page"] = request.headers.get("referer", "/incidents")

    return render(
        request,
        "regulator/incident_edit.html",
        context={
            "regulator_incident_form": regulator_incident_form,
            "incident": incident,
        },
    )


@login_required
@otp_required
def download_incident_pdf(request, incident_id: int):
    target = request.headers.get("referer", "/")
    if not can_redirect(target):
        target = "/"

    # RegulatorUser can access only incidents from accessible sectors.
    if (
        user_in_group(request.user, "RegulatorUser")
        and not Incident.objects.filter(
            pk=incident_id, affected_services__sector__in=request.user.sectors.all()
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")
    # OperatorAdmin can access only incidents related to selected company.
    if (
        user_in_group(request.user, "OperatorAdmin")
        and not Incident.objects.filter(
            pk=incident_id, company__id=request.session.get("company_in_use")
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")
    # OperatorStaff and IncidentUser can access only their reports.
    if (
        not is_user_regulator(request.user)
        and not user_in_group(request.user, "OperatorAdmin")
        and not Incident.objects.filter(
            pk=incident_id, contact_user=request.user
        ).exists()
    ):
        return HttpResponseRedirect("/incidents")

    incident = Incident.objects.get(pk=incident_id)

    try:
        pdf_report = get_pdf_report(incident, request)
    except Exception:
        messages.warning(request, _("An error occurred when generating the report."))
        return HttpResponseRedirect(target)

    response = HttpResponse(pdf_report, content_type="application/pdf")
    response["Content-Disposition"] = "attachment;filename=Incident_{}_{}.pdf".format(
        incident_id, date.today()
    )

    return response


def is_incidents_report_limit_reached(request):
    if request.user.is_authenticated:
        # if a user make too many declaration we prevent to save
        number_preliminary_today = Incident.objects.filter(
            contact_user=request.user, incident_notification_date=date.today()
        ).count()
        if number_preliminary_today >= MAX_PRELIMINARY_NOTIFICATION_PER_DAY_PER_USER:
            messages.warning(
                request,
                _(
                    "The incidents reports per day have been reached. Try again tomorrow."
                ),
            )
            return True
    return False


# remove a prefix on a multivaluedict object
def get_temporary_cleaned_data(MultivalueDict, prefix):
    for d in list(MultivalueDict):
        if d.startswith(prefix):
            MultivalueDict.setlist(d[2:], MultivalueDict.getlist(d))
            del MultivalueDict[d]
    return MultivalueDict


# if there are no sectors don't show sectors, condition dict for wizard
def show_sector_form_condition(wizard):
    data1 = wizard.storage.get_step_data("1")
    if data1 is not None:
        data1 = get_temporary_cleaned_data(data1, "1-")
    data2 = wizard.storage.get_step_data("2")
    if data2 is not None:
        data2 = get_temporary_cleaned_data(data2, "2-")
    temp_regulator_form = RegulatorForm(
        data=data1,
    )
    regulators = None
    if data1 is not None and data1["regulators"] is not None:
        regulators = Regulator.objects.all().filter(pk__in=data1.getlist("regulators"))
    temp_regulation_form = RegulationForm(
        data=data2, initial={"regulators": regulators}
    )
    data_regulation = data_regulator = None

    if temp_regulation_form.is_valid() and temp_regulator_form.is_valid():
        data_regulation = temp_regulation_form.cleaned_data
        data_regulator = temp_regulator_form.cleaned_data

    has_sector = False
    if data_regulator is not None and data_regulation is not None:
        ids = data_regulation.get("regulations", "")
        regulations = Regulation.objects.filter(id__in=ids)
        ids = data_regulator.get("regulators", "")
        regulators = Regulator.objects.filter(id__in=ids)
        sector_regulations = SectorRegulation.objects.all().filter(
            regulation__in=regulations, regulator__in=regulators
        )

        for sector_regulation in sector_regulations:
            for __sector in sector_regulation.sectors.all():
                has_sector = True
    return has_sector


class FormWizardView(SessionWizardView):
    """Wizard to manage the preliminary form."""

    template_name = "declaration.html"

    def __init__(self, **kwargs):
        self.form_list = kwargs.pop("form_list")
        self.initial_dict = kwargs.pop("initial_dict")
        return super().__init__(**kwargs)

    def get_form(self, step=None, data=None, files=None):
        # active_company = get_active_company_from_session(self.request)
        if step is None:
            step = self.steps.current

        form = super().get_form(step, data, files)
        return form

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        context["steps"] = [
            _("Contact"),
            _("Regulators"),
            _("Regulations"),
            _("Sectors"),
        ]

        return context

    def get_form_initial(self, step):
        if step == "2":
            step1data = self.get_cleaned_data_for_step("1")
            if step1data:
                ids = step1data.get("regulators", "")
                regulators = Regulator.objects.filter(id__in=ids)
                return self.initial_dict.get(step, {"regulators": regulators})
        if step == "3":
            step2data = self.get_cleaned_data_for_step("2")
            step1data = self.get_cleaned_data_for_step("1")
            if step2data:
                ids = step2data.get("regulations", "")
                regulations = Regulation.objects.filter(id__in=ids)
                ids = step1data.get("regulators", "")
                regulators = Regulator.objects.filter(id__in=ids)
                return self.initial_dict.get(
                    step, {"regulations": regulations, "regulators": regulators}
                )
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        if is_incidents_report_limit_reached(self.request):
            return HttpResponseRedirect("/incidents")

        data = [form.cleaned_data for form in form_list]
        user = self.request.user
        company = get_active_company_from_session(self.request)

        sectors_id = []
        if len(data) > 3:
            for sector_data in data[3]["sectors"]:
                try:
                    sector_id = int(sector_data)
                    sectors_id.append(sector_id)
                except Exception:
                    pass

        regulations_id = []
        for regulations_data in data[2]["regulations"]:
            try:
                regulation_id = int(regulations_data)
                regulations_id.append(regulation_id)
            except Exception:
                pass

        regulators_id = []
        for regulators_data in data[1]["regulators"]:
            try:
                regulator_id = int(regulators_data)
                regulators_id.append(regulator_id)
            except Exception:
                pass

        # get sector_regulations where the sectors is specified
        temps_ids = []
        if len(sectors_id) > 0:
            sector_regulations = SectorRegulation.objects.all().filter(
                sectors__in=sectors_id,
                regulator__in=regulators_id,
                regulation__in=regulations_id,
            )
            temps_ids = sector_regulations.values_list("id", flat=True)

        # add regulation without sector excluding the previous one
        sector_regulations2 = (
            SectorRegulation.objects.all()
            .filter(regulator__in=regulators_id, regulation__in=regulations_id)
            .exclude(id__in=temps_ids)
        )

        sector_regulations = sector_regulations | sector_regulations2

        for sector_regulation in sector_regulations:
            incident = Incident.objects.create(
                contact_lastname=data[0]["contact_lastname"],
                contact_firstname=data[0]["contact_firstname"],
                contact_title=data[0]["contact_title"],
                contact_email=data[0]["contact_email"],
                contact_telephone=data[0]["contact_telephone"],
                # technical contact
                technical_lastname=data[0]["technical_lastname"],
                technical_firstname=data[0]["technical_firstname"],
                technical_title=data[0]["technical_title"],
                technical_email=data[0]["technical_email"],
                technical_telephone=data[0]["technical_telephone"],
                incident_reference=data[0]["incident_reference"],
                complaint_reference=data[0]["complaint_reference"],
                contact_user=user,
                company=company,
                company_name=company.name if company else data[0]["company_name"],
                sector_regulation=sector_regulation,
            )
            affected_sectors = Sector.objects.filter(id__in=sectors_id)
            incident.affected_sectors.set(affected_sectors)
            # incident reference
            company_for_ref = ""
            sector_for_ref = ""
            subsector_for_ref = ""
            if company is None:
                company_for_ref = data[0]["company_name"][:4]
            else:
                company_for_ref = company.identifier

            for sector in sector_regulation.sectors.all():
                if sector.id in sectors_id:
                    if subsector_for_ref == "":
                        subsector_for_ref = sector.acronym[:3]
                        if sector.parent is not None:
                            sector_for_ref = sector.parent.acronym[:3]

            incidents_per_company = company.incident_set.count() + 1 if company else 0
            number_of_incident = f"{incidents_per_company:04}"
            incident.incident_id = (
                company_for_ref
                + "_"
                + sector_for_ref
                + "_"
                + subsector_for_ref
                + "_"
                + number_of_incident
                + "_"
                + str(date.today().year)
            )
            incident.save()

        # Send Email
        email = Email.objects.filter(email_type="PRELI").first()
        if email is not None:
            send_email(email, incident)
        return HttpResponseRedirect("/incidents")


class WorkflowWizardView(SessionWizardView):
    """Wizard to manage the different workflows."""

    template_name = "declaration.html"
    incident = None
    workflow = None
    incident_workflow = None

    def __init__(self, **kwargs):
        self.form_list = kwargs.pop("form_list")
        return super().__init__(**kwargs)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        position = int(step)
        if self.request.incident_workflow:
            self.incident_workflow = IncidentWorkflow.objects.get(
                pk=self.request.incident_workflow
            )
            self.incident = self.incident_workflow.incident
            self.workflow = self.incident_workflow.workflow
            form = QuestionForm(
                data,
                position=position,
                incident_workflow=self.incident_workflow,
            )
        elif self.request.incident:
            self.incident = Incident.objects.get(pk=self.request.incident)
            self.workflow = self.incident.get_next_step()
            form = QuestionForm(
                data,
                position=position,
                workflow=self.workflow,
            )

        return form

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        # TO DO : put the correct categories
        categories = QuestionCategory.objects.all().order_by("position").distinct()

        context["steps"] = []

        for categorie in categories:
            context["steps"].append(categorie.label)

        return context

    def done(self, form_list, **kwargs):
        data = [form.cleaned_data for form in form_list]
        if self.incident is None:
            self.incident = Incident.objects.get(pk=self.request.incident)

        # TO DO : send the email
        email = None

        self.incident.save()
        # manage question
        save_answers(0, data, self.incident, self.workflow)
        if email is not None:
            send_email(email, self.incident)
        return HttpResponseRedirect("/incidents")


def save_answers(index=0, data=None, incident=None, workflow=None):
    """Save the answers."""

    # We create a new incident workflow in all the case (history)
    incident_workflow = IncidentWorkflow.objects.create(
        incident=incident, workflow=workflow
    )
    for d in range(index, len(data)):
        for key, value in data[d].items():
            question_id = None
            try:
                question_id = int(key)
            except Exception:
                pass
            if question_id is not None:
                predefined_answers = []
                question = Question.objects.get(pk=key)
                if question.question_type == "FREETEXT":
                    answer = value
                elif question.question_type == "DATE":
                    if value is not None:
                        answer = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        answer = None
                elif question.question_type == "CL" or question.question_type == "RL":
                    answer = ""
                    for val in value:
                        answer += val + ","
                    answer = answer
                else:  # MULTI
                    for val in value:
                        predefined_answers.append(PredefinedAnswer.objects.get(pk=val))
                    answer = None
                    if data[d].get(key + "_answer"):
                        answer = data[d][key + "_answer"]
                answer_object = Answer.objects.create(
                    incident_workflow=incident_workflow,
                    question=question,
                    answer=answer,
                )
                answer_object.predefined_answers.set(predefined_answers)


def can_redirect(url: str) -> bool:
    """
    Check if a redirect is authorised.
    """
    o = urlparse(url)
    return o.netloc in PUBLIC_URL
