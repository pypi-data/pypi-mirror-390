import msal
import requests


class graph_emailer:
    def __init__(self, client_id, client_secret, tenant_id, sender, logger=None):
        self.logger = logger
        self.sender = sender
        self.access_token = None

        try:
            authority = f"https://login.microsoftonline.com/{tenant_id}"
            scopes = ["https://graph.microsoft.com/.default"]

            app = msal.ConfidentialClientApplication(
                client_id,
                authority=authority,
                client_credential=client_secret
            )

            result = app.acquire_token_for_client(scopes)

            if "access_token" in result:
                self.access_token = result["access_token"]
                if logger:
                    logger.debug("Successfully obtained Graph API token.")
            else:
                error_msg = result.get("error_description", str(result))
                if logger:
                    logger.error(f"Failed to get token: {error_msg}")

        except Exception as e:
            if logger:
                logger.error(f"GraphEmailer initialization failed: {e}")


    def send_email(self, logger, subject, content_type, body, to_field, cc_field=None, bcc_field=None, priority="normal"):
        try:
            if not self.access_token:
                logger.error(f"Invalid Access Token, email cannot be sent!")
                return -1
            
            def parse_recipients(field):
                if not field:
                    return []
                # Split by comma and strip spaces
                return [{"emailAddress": {"address": addr.strip()}} for addr in field.split(",") if addr.strip()]

            to_recipients = parse_recipients(to_field)
            cc_recipients = parse_recipients(cc_field)
            bcc_recipients = parse_recipients(bcc_field)

            valid_types = {"text": "Text", "plain": "Text", "html": "HTML", "text/plain": "Text", "text/html": "HTML"}
            content_type_normalized = valid_types.get(content_type.strip().lower(), "Text")

            # Send email via Microsoft Graph
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self.sender}/sendMail"
            email_msg = {
                "message": {
                    "subject": f"{subject}",
                    "body": {
                        "contentType": f"{content_type_normalized}",
                        "content": f"{body}"
                    },
                    "toRecipients": to_recipients,
                    "importance": priority
                }
            }

            if cc_recipients:
                email_msg["message"]["ccRecipients"] = cc_recipients
            if bcc_recipients:
                email_msg["message"]["bccRecipients"] = bcc_recipients

            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers, json=email_msg)

            if response.status_code == 202:
                logger.debug(f"send_email successful!")
                return 0
            else:
                logger.error(f"send_email failed: {response.status_code}, {response.text}")
                logger.debug(f"subject: {subject}, content_type: {content_type}, body: {body}")
                return -1
        except Exception as e:
            logger.error(f"send_email failed: {e}")
            return -1