from django.db import transaction
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from schedule.models import Event
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from travel_maker.public_data_collector.models import TravelInfo
from travel_maker.travel_schedule.models import TravelInfoEvent, TravelSchedule


class EventSerializer(ModelSerializer):
    id = IntegerField(label='ID', required=False)

    class Meta:
        model = Event
        fields = ('id', 'start', 'end', 'title', 'calendar')


class TravelInfoEventSerializer(ModelSerializer):
    id = IntegerField(label='ID', required=False)
    event = EventSerializer(many=False)
    travel_info = PrimaryKeyRelatedField(queryset=TravelInfo.objects.all())

    class Meta:
        model = TravelInfoEvent
        fields = ('id', 'event', 'travel_schedule', 'travel_info')


class TravelScheduleSerializer(ModelSerializer):
    travelinfoevent_set = TravelInfoEventSerializer(many=True)

    class Meta:
        model = TravelSchedule
        fields = ('calendar', 'travelinfoevent_set')

    @transaction.atomic
    def update(self, instance, validated_data):
        travel_info_events_data = validated_data.pop('travelinfoevent_set')
        instance.save()

        event_id_list = [
            travelinfoevent['event']['id'] for travelinfoevent in travel_info_events_data
            if travelinfoevent['event'].get('id')
        ]
        travelinfoevent_id_list = [
            travelinfoevent['id'] for travelinfoevent in travel_info_events_data
            if travelinfoevent.get('id')
        ]
        Event.objects.exclude(id__in=event_id_list).delete()
        TravelInfoEvent.objects.exclude(id__in=travelinfoevent_id_list).delete()

        for data in travel_info_events_data:
            event_data = data.pop('event')
            if event_data.get('id') and data.get('id'):
                Event.objects.filter(id=event_data['id']).update(**event_data)
                TravelInfoEvent.objects.filter(id=data['id']).update(**data)
            else:
                event = Event.objects.create(**event_data)
                TravelInfoEvent.objects.create(event=event, **data)

        return instance
