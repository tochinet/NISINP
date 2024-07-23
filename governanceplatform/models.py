from django.contrib import admin
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from parler.models import TranslatableModel, TranslatedFields
from phonenumber_field.modelfields import PhoneNumberField

import governanceplatform

from .managers import CustomUserManager


# sector
class Sector(TranslatableModel):
    translations = TranslatedFields(name=models.CharField(_("Name"), max_length=100))
    parent = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        verbose_name=_("parent"),
    )
    acronym = models.CharField(
        verbose_name=_("Acronym"), max_length=4, null=True, blank=True, default=None
    )

    # name of the regulator who create the object
    creator_name = models.CharField(
        verbose_name=_("Creator Name"),
        max_length=255,
        blank=True,
        default=None,
        null=True,
    )
    creator = models.ForeignKey(
        "governanceplatform.regulator",
        verbose_name=_("Creator"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        if self.name is not None and self.parent is not None:
            return self.parent.name + " --> " + self.name
        elif self.name is not None and self.parent is None:
            return self.name
        else:
            return ""

    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")


# esssential services
class Service(TranslatableModel):
    translations = TranslatedFields(name=models.CharField(_("Name"), max_length=100))
    sector = models.ForeignKey(
        Sector, verbose_name=_("Sector"), on_delete=models.CASCADE
    )
    acronym = models.CharField(
        verbose_name=_("Acronym"), max_length=4, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.name if self.name is not None else ""

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")


# functionality (e.g, risk analysis, SO)
class Functionality(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("Name"), max_length=100)
    )

    def __str__(self):
        return self.name if self.name is not None else ""

    class Meta:
        verbose_name = _("Functionality")
        verbose_name_plural = _("Functionalities")


# operator has type (critical, essential, etc.) who give access to functionalities
class OperatorType(TranslatableModel):
    translations = TranslatedFields(
        type=models.CharField(verbose_name=_("Type"), max_length=100)
    )
    functionalities = models.ManyToManyField(
        Functionality,
        verbose_name=_("Functionalities"),
    )

    def __str__(self):
        return self.type if self.type is not None else ""


# operator are companies
class Company(models.Model):
    identifier = models.CharField(
        max_length=4, verbose_name=_("Identifier")
    )  # requirement from business concat(name_country_regulator)
    name = models.CharField(max_length=64, verbose_name=_("name"))
    country = models.CharField(
        max_length=200,
        verbose_name=_("Country"),
        null=True,
        choices=list(CountryField().choices),
    )
    address = models.CharField(max_length=255, verbose_name=_("address"))
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("email address"),
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Phone number"),
        max_length=30,
        blank=True,
        default=None,
        null=True,
    )
    sector_contacts = models.ManyToManyField(
        Sector,
        through="SectorCompanyContact",
        verbose_name=_("Sector Contacts"),
    )

    types = models.ManyToManyField(
        OperatorType,
        verbose_name=_("Types"),
    )

    def __str__(self):
        return self.name

    @admin.display(description="sectors")
    def get_sectors(self):
        sectors = []
        for sector in self.sector_contacts.all().distinct():
            if sector.name is not None and sector.parent is not None:
                sectors.append(sector.parent.name + " --> " + sector.name)
            elif sector.name is not None and sector.parent is None:
                sectors.append(sector.name)

        return sectors

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


# Regulator
class Regulator(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=64, verbose_name=_("name")),
        full_name=models.TextField(
            blank=True, default="", null=True, verbose_name=_("full name")
        ),
        description=models.TextField(
            blank=True, default="", null=True, verbose_name=_("description")
        ),
    )
    country = models.CharField(
        max_length=200,
        null=True,
        choices=list(CountryField().choices),
        verbose_name=_("country"),
    )
    address = models.CharField(max_length=255, verbose_name=_("address"))
    email_for_notification = models.EmailField(
        verbose_name=_("email address for incident notification"),
        default=None,
        blank=True,
        null=True,
    )
    is_receiving_all_incident = models.BooleanField(
        default=False, verbose_name=_("Receive all incident")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Regulator")
        verbose_name_plural = _("Regulators")


# CERT
class Cert(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(default="", max_length=64, verbose_name=_("name")),
        full_name=models.TextField(
            blank=True, default="", null=True, verbose_name=_("full name")
        ),
        description=models.TextField(
            blank=True, default="", null=True, verbose_name=_("description")
        ),
    )
    country = models.CharField(
        max_length=200,
        null=True,
        choices=list(CountryField().choices),
        verbose_name=_("country"),
    )
    address = models.CharField(max_length=255, verbose_name=_("address"))
    email_for_notification = models.EmailField(
        verbose_name=_("email address for incident notification"),
        default=None,
        blank=True,
        null=True,
    )
    is_receiving_all_incident = models.BooleanField(
        default=False, verbose_name=_("Receive all incident")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("CERT")
        verbose_name_plural = _("CERTs")


# define an abstract class which make  the difference between operator and regulator
class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        verbose_name=_("email address"),
        unique=True,
        error_messages={
            "unique": _("A user is already registered with this email address"),
        },
    )
    phone_number = PhoneNumberField(
        max_length=30,
        blank=True,
        default=None,
        null=True,
        verbose_name=_("Phone number"),
    )
    companies = models.ManyToManyField(
        Company,
        through="SectorCompanyContact",
        verbose_name=_("Companies"),
    )
    sectors = models.ManyToManyField(
        Sector,
        through="SectorCompanyContact",
        verbose_name=_("Sectors"),
    )
    regulators = models.ManyToManyField(
        Regulator,
        through="RegulatorUser",
        verbose_name=_("Regulators"),
    )
    certs = models.ManyToManyField(
        Cert,
        through="CertUser",
        verbose_name=_("Certs"),
    )

    is_staff = models.BooleanField(
        verbose_name=_("Administrator"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    # @admin.display(description="sectors")
    # def get_sectors(self):
    #     return [sector.name for sector in self.sectors.all()]

    @admin.display(description="companies")
    def get_companies(self):
        return [company.name for company in self.companies.all().distinct()]

    @admin.display(description="regulators")
    def get_regulators(self):
        return [regulator.name for regulator in self.regulators.all()]

    @admin.display(description="certs")
    def get_certs(self):
        return [cert.name for cert in self.certs.all()]

    @admin.display(description="Roles")
    def get_permissions_groups(self):
        return ", ".join([group.name for group in self.groups.all()])

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def get_sectors(self):
        if governanceplatform.helpers.user_in_group(self, "RegulatorUser"):
            ru = RegulatorUser.objects.filter(user=self).first()
            return ru.sectors
        else:
            return self.sectors

    class Meta:
        permissions = (
            ("import_user", "Can import user"),
            ("export_user", "Can export user"),
        )


class SectorCompanyContact(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        verbose_name=_("Sector"),
    )
    is_sector_contact = models.BooleanField(
        default=False, verbose_name=_("Contact person")
    )
    is_company_administrator = models.BooleanField(
        default=False, verbose_name=_("is administrator")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "sector", "company"], name="unique_SectorCompanyContact"
            ),
        ]
        verbose_name = _("Sector contact")
        verbose_name_plural = _("Sectors contact")

    def __str__(self):
        return ""


# link between the admin regulator users and the regulators.
class RegulatorUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    regulator = models.ForeignKey(
        Regulator,
        on_delete=models.CASCADE,
        verbose_name=_("Regulator"),
    )
    is_regulator_administrator = models.BooleanField(
        default=False, verbose_name=_("is administrator")
    )
    sectors = models.ManyToManyField(Sector, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "regulator"], name="unique_RegulatorUser"
            ),
        ]
        verbose_name = _("Regulator user")
        verbose_name_plural = _("Regulator users")

    def __str__(self):
        return ""


# link between the admin cert users and the cert.
class CertUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    cert = models.ForeignKey(
        Cert,
        on_delete=models.CASCADE,
        verbose_name=_("Cert"),
    )
    is_cert_administrator = models.BooleanField(
        default=False, verbose_name=_("is administrator")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "cert"], name="unique_CertUser"),
        ]
        verbose_name = _("CERT user")
        verbose_name_plural = _("CERT users")

    def __str__(self):
        return ""


# Different regulation like NIS etc.
class Regulation(TranslatableModel):
    translations = TranslatedFields(
        label=models.CharField(
            max_length=255,
            blank=True,
            default=None,
            null=True,
            verbose_name=_("Label"),
        )
    )
    regulators = models.ManyToManyField(
        Regulator,
        default=None,
        blank=True,
        verbose_name=_("Regulators"),
    )

    @admin.display(description="regulators")
    def get_regulators(self):
        return [regulator.name for regulator in self.regulators.all()]

    def __str__(self):
        return self.label if self.label is not None else ""
