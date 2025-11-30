from django import forms
from django.forms import BaseInlineFormSet
from .models import Challenge
from workouts.models import Exercise
from django.utils import timezone
from datetime import timedelta


def get_challenge_exercise_formset(extra=3, initial=None):
    """Factory function to create exercise formset with variable extra forms"""
    
    class ChallengeExerciseForm(forms.Form):
        """Form for a single exercise within a challenge"""
        exercise = forms.ModelChoiceField(
            queryset=Exercise.objects.all().order_by('name'),
            required=True,
            help_text="Select an exercise from the database",
            widget=forms.Select(attrs={
                'class': 'exercise-select',
                'data-placeholder': 'Choose an exercise...'
            })
        )
        sets = forms.IntegerField(
            min_value=1,
            max_value=10,
            initial=3,
            help_text="Number of sets",
            widget=forms.NumberInput(attrs={'class': 'sets-input'})
        )
        reps = forms.IntegerField(
            min_value=0,
            max_value=100,
            initial=10,
            required=False,
            help_text="Number of reps per set (leave empty for timed exercises)",
            widget=forms.NumberInput(attrs={'class': 'reps-input'})
        )
        duration_seconds = forms.IntegerField(
            min_value=0,
            max_value=3600,
            required=False,
            help_text="Duration in seconds (for timed exercises like planks)",
            widget=forms.NumberInput(attrs={'class': 'duration-input'})
        )
        rest_time = forms.IntegerField(
            min_value=0,
            max_value=300,
            initial=60,
            help_text="Rest time between sets (seconds)",
            widget=forms.NumberInput(attrs={'class': 'rest-input'})
        )
        notes = forms.CharField(
            required=False,
            max_length=500,
            widget=forms.Textarea(attrs={
                'rows': 2,
                'class': 'notes-input',
                'placeholder': 'Add specific instructions for this exercise...'
            }),
            help_text="Optional notes or instructions"
        )
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add custom classes for styling
            for field_name, field in self.fields.items():
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
    
    class BaseChallengeExerciseFormSet(forms.BaseFormSet):
        """Custom formset for challenge exercises"""
        
        def clean(self):
            """Validate that at least one exercise is added"""
            if any(self.errors):
                return
            
            if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) 
                       for form in self.forms):
                raise forms.ValidationError('A challenge must have at least one exercise.')
    
    # Create and return the formset
    FormSet = forms.formset_factory(
        ChallengeExerciseForm,
        formset=BaseChallengeExerciseFormSet,
        extra=extra,
        can_delete=True,
        can_order=False
    )
    
    return FormSet


class ChallengeAdminForm(forms.ModelForm):
    """Custom form for Challenge creation in admin"""
    
    # Override start_date and end_date with better defaults
    start_date = forms.DateTimeField(
        initial=lambda: timezone.now(),
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text="When the challenge becomes available"
    )
    
    end_date = forms.DateTimeField(
        initial=lambda: timezone.now() + timedelta(days=1),
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text="When the challenge expires"
    )
    
    class Meta:
        model = Challenge
        fields = [
            'name', 'description', 'challenge_type', 'difficulty',
            'completion_points', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Morning Power Challenge'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the challenge...'
            }),
            'challenge_type': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'completion_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make created_by automatically set to current user
        if 'created_by' in self.fields:
            self.fields['created_by'].required = False
        
        # If editing existing challenge, load exercises into formset data
        if self.instance.pk and self.instance.exercises:
            self.initial_exercises = self.instance.exercises
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set created_by to current user if not set
        if not instance.created_by_id and hasattr(self, 'current_user'):
            instance.created_by = self.current_user
        
        # Note: exercises will be set separately by the admin class
        
        if commit:
            instance.save()
        
        return instance

