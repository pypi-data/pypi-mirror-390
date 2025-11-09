|pypi| |actions| |codecov| |downloads|

edc-he
------

Health economics model, form mixins for clinicedc / Django


Declare in `settings` if using concrete models not included in this app::

    EDC_HE_ASSETS_MODEL = "<label_lower>"
    EDC_HE_HOUSEHOLDHEAD_MODEL = "<label_lower>"
    EDC_HE_INCOME_MODEL = "<label_lower>"
    EDC_HE_PATIENT_MODEL = "<label_lower>"
    EDC_HE_PROPERTY_MODEL = "<label_lower>"

See also module ``intecomm_subject`` at https://github.com/intecomm-trial/intecomm-edc.

If you need to declare the Health Economics models in your app, use the provided model mixins.

For example, the ``HealthEconomicsHouseholdHead`` model would be declared like this:

.. code-block:: python

    # models.py

    class HealthEconomicsHouseholdHead(
        SingletonCrfModelMixin,
        HouseholdHeadModelMixin,
        HouseholdModelMixin,
        CrfModelMixin,
        BaseUuidModel,
    ):

        class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Health Economics: Household head"
            verbose_name_plural = "Health Economics: Household head"


.. code-block:: python

    # forms.py

    class HealthEconomicsHouseholdHeadForm(
        CrfSingletonModelFormMixin, CrfModelFormMixin, forms.ModelForm
    ):
        form_validator_cls = HealthEconomicsHouseholdHeadFormValidator

        def clean(self):
            self.raise_if_singleton_exists()
            raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
            return super().clean()

.. code-block:: python

    # admin.py


    @admin.register(HealthEconomicsHouseholdHead, site=intecomm_subject_admin)
    class HealthEconomicsHouseholdHeadAdmin(
        HealthEconomicsHouseholdHeadModelAdminMixin, CrfModelAdmin
    ):
        form = HealthEconomicsHouseholdHeadForm


The metadata rules may also be declared locally


.. code-block:: python

    # metadata_rules.py

    from edc_he.rule_groups import Predicates as BaseHealthEconomicsPredicates
    from edc_he.rule_groups import HealthEconomicsRuleGroup as BaseHealthEconomicsRuleGroup

    class HealthEconomicsPredicates(BaseHealthEconomicsPredicates):
        app_label = "intecomm_subject"
        visit_model = "intecomm_subject.subjectvisit"

    @register()
    class HealthEconomicsRuleGroup(BaseHealthEconomicsRuleGroup):
        class Meta:
            app_label = "intecomm_subject"
            source_model = "intecomm_subject.subjectvisit"
            predicates = HealthEconomicsPredicates()



.. |pypi| image:: https://img.shields.io/pypi/v/edc-he.svg
    :target: https://pypi.python.org/pypi/edc-he

.. |actions| image:: https://github.com/clinicedc/edc-he/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-he/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-he/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-he

.. |downloads| image:: https://pepy.tech/badge/edc-he
   :target: https://pepy.tech/project/edc-he
