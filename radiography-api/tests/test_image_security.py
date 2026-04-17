import unittest
from datetime import timedelta

from fastapi import HTTPException

from app.core.security import create_image_access_token, verify_image_access_token
from app.schemas.auth_schema import UserResponse


class ImageSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.user = UserResponse(
            email="test@example.com",
            name="Test User",
            google_id="google-user-123",
        )

    def test_image_token_is_valid_for_matching_user_and_image(self) -> None:
        token = create_image_access_token(image_id=7, user=self.user)

        payload = verify_image_access_token(
            token=token,
            image_id=7,
            user=self.user,
        )

        self.assertEqual(payload["image_id"], 7)
        self.assertEqual(payload["google_id"], self.user.google_id)

    def test_image_token_fails_for_different_image(self) -> None:
        token = create_image_access_token(image_id=7, user=self.user)

        with self.assertRaises(HTTPException) as context:
            verify_image_access_token(
                token=token,
                image_id=8,
                user=self.user,
            )

        self.assertEqual(context.exception.status_code, 401)

    def test_image_token_fails_for_different_user(self) -> None:
        token = create_image_access_token(image_id=7, user=self.user)
        other_user = UserResponse(
            email="other@example.com",
            name="Other User",
            google_id="other-google-user",
        )

        with self.assertRaises(HTTPException) as context:
            verify_image_access_token(
                token=token,
                image_id=7,
                user=other_user,
            )

        self.assertEqual(context.exception.status_code, 401)

    def test_image_token_fails_after_expiration(self) -> None:
        token = create_image_access_token(
            image_id=7,
            user=self.user,
            expires_delta=timedelta(seconds=-1),
        )

        with self.assertRaises(HTTPException) as context:
            verify_image_access_token(
                token=token,
                image_id=7,
                user=self.user,
            )

        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
