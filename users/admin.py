from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	"""Admin configuration for the custom User model."""

	# Show extra fields in list view (optional)
	list_display = (
		"username",
		"email",
		"first_name",
		"last_name",
		"is_staff",
		"age",
		"can_be_contacted",
		"can_data_be_shared",
	)

	# Add custom fields into the user detail edit page
	fieldsets = (
		(None, {"fields": ("username", "password")}),
		(_("Personal info"), {"fields": ("first_name", "last_name", "email", "age")}),
		(
			_("Permissions"),
			{
				"fields": (
					"is_active",
					"is_staff",
					"is_superuser",
					"groups",
					"user_permissions",
				)
			},
		),
		(_("Privacy & contact"), {"fields": ("can_be_contacted", "can_data_be_shared")}),
		(_("Important dates"), {"fields": ("last_login", "date_joined")}),
	)

	# Include custom fields on the user creation page in admin
	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": (
					"username",
					"password1",
					"password2",
					"email",
					"first_name",
					"last_name",
					"age",
					"can_be_contacted",
					"can_data_be_shared",
				),
			},
		),
	)

