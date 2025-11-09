from rest_framework import serializers

from ichec_django_core.serializers import (
    NestedHyperlinkedModelSerializer,
    PopulatedFormSerializer,
)

from marinerg_test_access.models import AccessApplication


class AccessApplicationBaseSerializer(NestedHyperlinkedModelSerializer):

    form = PopulatedFormSerializer()

    class Meta:
        model = AccessApplication
        fields = (
            "facilities",
            "request_start_date",
            "request_end_date",
            "dates_flexible",
            "call",
            "form",
            "status",
        )


class AccessApplicationDetailSerializer(AccessApplicationBaseSerializer):

    call_title = serializers.CharField(
        source="call.title", required=False, read_only=True
    )
    applicant_username = serializers.CharField(
        source="applicant.username", required=False, read_only=True
    )

    class Meta:
        model = AccessApplication
        fields = (
            tuple(AccessApplicationBaseSerializer.Meta.fields)
            + NestedHyperlinkedModelSerializer.base_fields
            + (
                "chosen_facility",
                "summary_url",
                "applicant",
                "call",
                "submitted",
                "call_title",
                "applicant_username",
            )
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + (
            "submitted",
            "applicant",
            "call_title",
            "summary_url",
            "applicant_username",
        )


class AccessApplicationCreateSerializer(AccessApplicationBaseSerializer):

    class Meta:
        model = AccessApplication
        fields = AccessApplicationBaseSerializer.Meta.fields

    def create(self, validated_data):

        form = validated_data.pop("form")
        form_instance = PopulatedFormSerializer().create(form)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = AccessApplication.objects.create(
            form=form_instance, **validated_data
        )
        self.add_many_to_many(instance, many_to_many)
        return instance

    def to_representation(self, instance):
        return AccessApplicationDetailSerializer(
            context=self.context
        ).to_representation(instance)
