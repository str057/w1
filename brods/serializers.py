from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from drf_spectacular.types import OpenApiTypes

from brods.models import Course, Lesson, Subscription, Payment
from brods.validators import URLValidator, validate_youtube_links


@extend_schema_serializer(
    examples=[
        {
            "title": "Основы Python",
            "description": "Изучение базовых концепций Python с YouTube видео: "
            "https://www.youtube.com/watch?v=abc123",
            "video_link": "https://www.youtube.com/watch?v=abc123",
            "course": 1,
            "order": 1,
        }
    ]
)
class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    video_link = serializers.URLField(
        validators=[validate_youtube_links], required=False, allow_blank=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [URLValidator(field="description")]


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "preview",
            "video_link",
            "course",
            "order",
        ]


@extend_schema_serializer(
    examples=[
        {
            "title": "Python для начинающих",
            "description": "Полный курс по основам Python",
            "price": "99.99",
        }
    ]
)
class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "price",
            "lessons_count",
            "is_subscribed",
            "owner",
            "created_at",
        ]
        validators = [URLValidator(field="description")]

    @extend_schema_field(OpenApiTypes.INT)
    def get_lessons_count(self, obj):
        return obj.lessons.count()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "price",
            "lessons",
            "is_subscribed",
            "owner",
            "created_at",
        ]

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    paid_course_title = serializers.CharField(
        source="paid_course.title", read_only=True
    )
    paid_lesson_title = serializers.CharField(
        source="paid_lesson.title", read_only=True
    )
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "paid_course",
            "paid_course_title",
            "paid_lesson",
            "paid_lesson_title",
            "amount",
            "payment_method",
            "payment_status",
            "stripe_session_id",
        ]
        read_only_fields = ["user", "payment_date", "payment_status"]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "amount", "payment_method"]

    def validate(self, attrs):
        if attrs.get("paid_course") and attrs.get("paid_lesson"):
            raise serializers.ValidationError(
                "Можно указать только курс ИЛИ урок, но не оба одновременно."
            )
        if not attrs.get("paid_course") and not attrs.get("paid_lesson"):
            raise serializers.ValidationError(
                "Должен быть указан либо курс, либо урок."
            )
        return attrs
