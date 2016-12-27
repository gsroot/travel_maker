from django.db import transaction
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from schedule.models import Event
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from travel_maker.public_data_collector.models import TravelInfo
from travel_maker.travel_schedule.models import TravelInfoEvent, TravelSchedule


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ('start', 'end', 'title', 'calendar')


class TravelInfoEventSerializer(ModelSerializer):
    event = EventSerializer(many=False)
    travel_info = PrimaryKeyRelatedField(queryset=TravelInfo.objects.all())

    class Meta:
        model = TravelInfoEvent
        fields = ('event', 'travel_schedule', 'travel_info')


class TravelScheduleSerializer(ModelSerializer):
    travelinfoevent_set = TravelInfoEventSerializer(many=True)

    class Meta:
        model = TravelSchedule
        fields = ('calendar', 'travelinfoevent_set')

    @transaction.atomic
    def update(self, instance, validated_data):
        travel_info_events_data = validated_data.pop('travelinfoevent_set')
        instance.save()

        Event.objects.filter(calendar=validated_data['calendar']).delete()
        TravelInfoEvent.objects.filter(travel_schedule__calendar=validated_data['calendar']).delete()

        for data in travel_info_events_data:
            event_data = data.pop('event')
            event = Event.objects.create(**event_data)
            TravelInfoEvent.objects.create(event=event, **data)

        return instance
