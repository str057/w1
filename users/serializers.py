from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import Payment, User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "city",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
        ]


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
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    item_type = serializers.SerializerMethodField()
    item_title = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_date",
            "item_type",
            "item_title",
            "amount",
            "payment_method",
        ]

    def get_item_type(self, obj):
        return "Курс" if obj.paid_course else "Урок"

    def get_item_title(self, obj):
        return obj.paid_course.title if obj.paid_course else obj.paid_lesson.title


class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = PaymentHistorySerializer(
        many=True, read_only=True, source="payments"
    )
    is_moderator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
            "is_moderator",
            "payment_history",
        ]
        read_only_fields = ["email", "date_joined", "is_moderator"]

    def get_is_moderator(self, obj):
        return obj.groups.filter(name="moderators").exists()


class UserProfilePublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного просмотра профиля"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "city",
            "avatar",
            "date_joined",
        ]
