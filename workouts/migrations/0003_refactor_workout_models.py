# Generated migration for refactoring workout models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0002_workout_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Rename Workout.title to Workout.name
        migrations.RenameField(
            model_name='workout',
            old_name='title',
            new_name='name',
        ),
        
        # Step 2: Add new fields to Workout with defaults
        migrations.AddField(
            model_name='workout',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workout',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='workout',
            name='estimated_calories',
            field=models.IntegerField(blank=True, help_text='Estimated calories burned', null=True),
        ),
        migrations.AddField(
            model_name='workout',
            name='estimated_duration',
            field=models.IntegerField(blank=True, help_text='Estimated duration in minutes', null=True),
        ),
        
        # Step 3: Migrate data from old fields to new fields
        migrations.RunSQL(
            sql='UPDATE workouts SET estimated_calories = calories_burn WHERE calories_burn IS NOT NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql='UPDATE workouts SET estimated_duration = duration_minutes WHERE duration_minutes IS NOT NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 4: Remove old fields from Workout
        migrations.RemoveField(
            model_name='workout',
            name='calories_burn',
        ),
        migrations.RemoveField(
            model_name='workout',
            name='duration_minutes',
        ),
        migrations.RemoveField(
            model_name='workout',
            name='user',
        ),
        
        # Step 5: Alter Workout meta options
        migrations.AlterModelOptions(
            name='workout',
            options={'ordering': ['name'], 'verbose_name': 'Workout', 'verbose_name_plural': 'Workouts'},
        ),
        migrations.AlterField(
            model_name='workout',
            name='video_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        
        # Step 6: Add new fields to Exercise
        migrations.AddField(
            model_name='exercise',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='duration_seconds',
            field=models.IntegerField(blank=True, help_text='Duration in seconds (for timed exercises)', null=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='order',
            field=models.IntegerField(default=0, help_text='Order of exercise in workout'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='rest_time',
            field=models.IntegerField(default=60, help_text='Rest time in seconds between sets'),
            preserve_default=False,
        ),
        
        # Step 7: Rename rest_seconds to prepare for migration
        migrations.RenameField(
            model_name='exercise',
            old_name='rest_seconds',
            new_name='rest_time_old',
        ),
        
        # Step 8: Migrate data from old rest_seconds field
        migrations.RunSQL(
            sql='UPDATE exercises SET rest_time = rest_time_old WHERE rest_time_old IS NOT NULL',
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 9: Remove old field
        migrations.RemoveField(
            model_name='exercise',
            name='rest_time_old',
        ),
        
        # Step 10: Add workout FK to Exercise (temporarily nullable)
        migrations.AddField(
            model_name='exercise',
            name='workout',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='workouts.workout'),
        ),
        
        # Step 11: Migrate exercises to workouts
        # This will link exercises to workouts through their rounds
        migrations.RunSQL(
            sql='''
                UPDATE exercises 
                SET workout_id = (
                    SELECT workout_id 
                    FROM workout_rounds 
                    WHERE workout_rounds.id = exercises.round_id
                )
                WHERE exercises.round_id IS NOT NULL
            ''',
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 12: Remove old round FK and make workout FK non-nullable
        migrations.RemoveField(
            model_name='exercise',
            name='round',
        ),
        migrations.AlterField(
            model_name='exercise',
            name='workout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='workouts.workout'),
        ),
        
        # Step 13: Update Exercise fields
        migrations.AlterField(
            model_name='exercise',
            name='reps',
            field=models.IntegerField(blank=True, help_text='Number of repetitions per set', null=True),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='sets',
            field=models.IntegerField(default=3, help_text='Default number of sets'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exercise',
            name='video_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        
        # Step 14: Alter Exercise meta options
        migrations.AlterModelOptions(
            name='exercise',
            options={'ordering': ['order'], 'verbose_name': 'Exercise', 'verbose_name_plural': 'Exercises'},
        ),
        
        # Step 15: Create new models
        migrations.CreateModel(
            name='UserWorkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by_ai', models.BooleanField(default=False, help_text='Whether this was assigned by AI')),
                ('custom_notes', models.TextField(blank=True, help_text='AI-generated or custom notes', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_workouts', to=settings.AUTH_USER_MODEL)),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assignments', to='workouts.workout')),
            ],
            options={
                'verbose_name': 'User Workout',
                'verbose_name_plural': 'User Workouts',
                'db_table': 'user_workouts',
                'ordering': ['-assigned_at'],
                'unique_together': {('user', 'workout')},
            },
        ),
        migrations.CreateModel(
            name='UserExerciseCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_sets', models.IntegerField(blank=True, null=True)),
                ('custom_reps', models.IntegerField(blank=True, null=True)),
                ('custom_duration_seconds', models.IntegerField(blank=True, null=True)),
                ('custom_rest_time', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workouts.exercise')),
                ('user_workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_customizations', to='workouts.userworkout')),
            ],
            options={
                'verbose_name': 'User Exercise Customization',
                'verbose_name_plural': 'User Exercise Customizations',
                'db_table': 'user_exercise_customizations',
                'unique_together': {('user_workout', 'exercise')},
            },
        ),
        migrations.CreateModel(
            name='WorkoutProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('completed_exercises', models.JSONField(default=list, help_text='List of completed exercise IDs')),
                ('actual_duration', models.IntegerField(blank=True, help_text='Actual duration in minutes', null=True)),
                ('actual_calories', models.FloatField(blank=True, help_text='Actual calories burned', null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('rating', models.IntegerField(blank=True, help_text='User rating (1-5)', null=True)),
                ('user_workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='workouts.userworkout')),
            ],
            options={
                'verbose_name': 'Workout Progress',
                'verbose_name_plural': 'Workout Progress Records',
                'db_table': 'workout_progress',
                'ordering': ['-completed_at'],
            },
        ),
        
        # Step 16: Delete old models
        migrations.DeleteModel(
            name='UserWorkoutProgress',
        ),
        migrations.RemoveField(
            model_name='workoutround',
            name='workout',
        ),
        migrations.DeleteModel(
            name='WorkoutRound',
        ),
    ]
