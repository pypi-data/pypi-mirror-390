from rest_framework import serializers

from ichec_django_core.serializers import (
    NestedHyperlinkedModelSerializer,
    FormSerializer,
)

from marinerg_test_access.models import AccessCall, AccessCallFacilityReview


class AccessCallBaseSerializer(NestedHyperlinkedModelSerializer):

    class Meta:
        model = AccessCall
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "title",
            "description",
            "status",
            "closing_date",
            "coordinator",
            "board_chair",
            "board_members",
            "selectable_facilities",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields


class AccessCallDetailSerializer(AccessCallBaseSerializer):

    form = FormSerializer()
    applications_summary = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="application_summaries"
    )

    class Meta:
        model = AccessCall
        fields = AccessCallBaseSerializer.Meta.fields + (
            "form",
            "applications_summary",
        )
        read_only_fields = AccessCallBaseSerializer.Meta.read_only_fields + (
            "applications_summary",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.applications_summary:
            rep["applications_summary"] = None
        return rep


class AccessCallCreateSerializer(AccessCallBaseSerializer):

    form = FormSerializer()

    class Meta:
        model = AccessCall
        fields = AccessCallBaseSerializer.Meta.fields + ("form",)
        read_only_fields = AccessCallBaseSerializer.Meta.read_only_fields

    def create(self, validated_data):

        form = validated_data.pop("form")
        form_instance = FormSerializer().create(form)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = AccessCall.objects.create(form=form_instance, **validated_data)
        self.add_many_to_many(instance, many_to_many)
        return instance

    def to_representation(self, instance):
        return AccessCallDetailSerializer(context=self.context).to_representation(
            instance
        )


class AccessCallListSerializer(AccessCallBaseSerializer):

    pass


class AccessCallFacilityReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessCallFacilityReview
        fields = ["decision", "comments", "call", "facility"]
