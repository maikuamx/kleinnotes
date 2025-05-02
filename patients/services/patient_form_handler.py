from django.db import transaction
from patients.models import Parent, Sibling, HouseholdMember, MedicalHistory

class PatientFormHandler:
    def __init__(self, request, patient):
        self.request = request
        self.patient = patient
        self.post_data = request.POST

    @transaction.atomic
    def handle_medical_history(self):
        medical_data = {}
        for key, value in self.post_data.items():
            if key.startswith('medical_') and value:
                field_name = key.replace('medical_', '')
                medical_data[field_name] = value
        
        if medical_data:
            MedicalHistory.objects.update_or_create(
                patient=self.patient,
                defaults=medical_data
            )

    @transaction.atomic
    def handle_family_members(self):
        # Limpiar datos existentes
        self.patient.parents.all().delete()
        self.patient.siblings.all().delete()
        self.patient.household_members.all().delete()

        # Procesar padres
        parent_names = self.post_data.getlist('parent_name[]')
        parent_birth_dates = self.post_data.getlist('parent_birth_date[]')
        parent_education_levels = self.post_data.getlist('parent_education_level[]')
        parent_occupations = self.post_data.getlist('parent_occupation[]')
        parent_pathological_histories = self.post_data.getlist('parent_pathological_history[]')

        for i in range(len(parent_names)):
            if parent_names[i]:
                Parent.objects.create(
                    patient=self.patient,
                    name=parent_names[i],
                    birth_date=parent_birth_dates[i],
                    education_level=parent_education_levels[i],
                    occupation=parent_occupations[i],
                    pathological_history=parent_pathological_histories[i]
                )

        # Procesar hermanos
        sibling_names = self.post_data.getlist('sibling_name[]')
        sibling_birth_dates = self.post_data.getlist('sibling_birth_date[]')
        sibling_education_levels = self.post_data.getlist('sibling_education_level[]')
        sibling_has_addictions = self.post_data.getlist('sibling_has_addictions[]')
        sibling_pathological_histories = self.post_data.getlist('sibling_pathological_history[]')

        for i in range(len(sibling_names)):
            if sibling_names[i]:
                Sibling.objects.create(
                    patient=self.patient,
                    name=sibling_names[i],
                    birth_date=sibling_birth_dates[i],
                    education_level=sibling_education_levels[i],
                    has_addictions=bool(sibling_has_addictions[i] if i < len(sibling_has_addictions) else False),
                    pathological_history=sibling_pathological_histories[i]
                )

        # Procesar habitantes del hogar
        household_names = self.post_data.getlist('household_name[]')
        household_relationships = self.post_data.getlist('household_relationship[]')
        household_medical_histories = self.post_data.getlist('household_medical_history[]')

        for i in range(len(household_names)):
            if household_names[i]:
                HouseholdMember.objects.create(
                    patient=self.patient,
                    name=household_names[i],
                    relationship=household_relationships[i],
                    medical_history=household_medical_histories[i]
                )