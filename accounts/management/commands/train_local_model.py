from django.core.management.base import BaseCommand

from ai_core.model_training import train_model


class Command(BaseCommand):
    help = "Train the local AgentPulse machine-learning model"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING("Starting model training...")
        )

        result = train_model()

        if result.get("success"):
            self.stdout.write(
                self.style.SUCCESS(result["message"])
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    result.get(
                        "message",
                        "Model training failed.",
                    )
                )
            )