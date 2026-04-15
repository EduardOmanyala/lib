from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmTokenGenerator(PasswordResetTokenGenerator):
    """Signed token for email confirmation; invalidates after email_verified changes."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email}{user.email_verified}"


email_confirm_token = EmailConfirmTokenGenerator()
