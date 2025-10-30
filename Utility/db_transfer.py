# utils/db_transfer.py
import json
from django.core import serializers
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder

def export_data(output_file='data.json'):
    """Export all model data to a JSON file with datetime support"""
    models_to_export = [
        # Account models
        ('Account', 'Plan'),
        ('Account', 'Account'),
        
        # Core models
        ('Category', 'Category'),
        ('Country', 'Country'),
        ('Tag', 'Tag'),
        ('Person', 'Person'),
        
        # Movie-related models
        ('Movie', 'Franchise'),
        ('Movie', 'Movie'),
        ('Movie', 'Video'),
        ('Movie', 'Subtitle'),
        ('Movie', 'Audio'),
        ('Movie', 'Trailer'),
        
        # List models
        ('Lists', 'List'),
        ('Lists', 'Item'),
        
        # Serial-related models
        ('Serial', 'Serial'),
        ('Serial', 'Season'),
        ('Serial', 'Episode'),
        ('Serial', 'EpisodeSubtitle'),
        ('Serial', 'SeasonSubtitle'),
        ('Serial', 'Audio'),  # Serial Audio
        ('Serial', 'Trailer'),  # Serial Trailer
    ]
    
    data = []
    
    for app_label, model_name in models_to_export:
        try:
            model = apps.get_model(app_label, model_name)
            # Use 'natural' mode for foreign keys and M2M relations
            serialized = serializers.serialize(
                'python', 
                model.objects.all(), 
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True
            )
            data.extend(serialized)
        except LookupError:
            print(f"Model {app_label}.{model_name} not found")
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, cls=DjangoJSONEncoder)  # Use Django's encoder

def import_data(input_file='data.json'):
    """Import data from JSON file with proper deserialization"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    for entry in data:
        try:
            # Handle datetime deserialization
            obj = serializers.deserialize('python', [entry])
            for item in obj:
                item.save()
        except Exception as e:
            print(f"Error importing {entry['pk']}: {str(e)}")