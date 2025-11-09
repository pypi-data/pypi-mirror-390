import json
import logging
from oqclib.utils.http_util import send_post_request_with_retries

logger = logging.getLogger(__name__)


class SlackMsg():
    def __init__(self, keys_dict):
        """
        Initialize Slack message sender
        :param keys_dict: Dictionary of Slack webhook URLs
        """
        self.keys_dict = keys_dict
        # Slack webhook URLs are typically in the format: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
        # We'll expect the full URL in the keys_dict

    def show_slack(self):
        """
        Show available Slack config
        :return: Slack keys available in config
        """
        print(self.keys_dict.keys())

    def send_msg(self, robot: str, msg: str):
        """
        Send a simple text message to Slack
        :param robot: Slack key name as defined in config
        :param msg: Message to send
        :return: Response from Slack API
        """
        webhook_url = self.keys_dict.get(robot)
        if not webhook_url:
            logger.error(f"Slack webhook URL for '{robot}' not found in config")
            return None

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        # Format message for Slack
        text_msg = {
            'text': msg
        }

        se = json.dumps(text_msg)
        logger.info(f"Sending message to Slack: {msg}")
        response = send_post_request_with_retries(webhook_url, se, headers=headers)
        
        if response:
            return response.text if response.text else {}
        return {}

    def send_card(self, robot: str, card_body: dict):
        """
        Send a rich message card to Slack
        :param robot: Slack key name as defined in config
        :param card_body: Dictionary containing the card details
                          Should follow Slack's Block Kit format
        :return: Response from Slack API
        """
        webhook_url = self.keys_dict.get(robot)
        if not webhook_url:
            logger.error(f"Slack webhook URL for '{robot}' not found in config")
            return None

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        # For Slack, we'll use the Block Kit format
        # Ensure the card_body follows the correct structure
        # See: https://api.slack.com/block-kit
        payload = {
            'blocks': card_body.get('blocks', [])
        }

        # If blocks are not provided but a text is, use the simple message format
        if not payload['blocks'] and 'text' in card_body:
            payload = {'text': card_body['text']}

        se = json.dumps(payload)
        logger.info(f"Sending card to Slack: {payload}")
        response = send_post_request_with_retries(webhook_url, se, headers=headers)
        
        if response:
            return response.text if response.text else {}
        return {}


# Helper function to create a basic Slack card
def create_basic_slack_card(title, message, color=None):
    """
    Create a basic Slack card structure
    :param title: Card title
    :param message: Card message content
    :param color: Optional color for the card border
    :return: Dictionary with Slack Block Kit structure
    """
    blocks = []
    
    # Add title as a section block
    if title:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{title}*"
            }
        })
    
    # Add message as a section block
    if message:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        })
    
    # Create the final card structure
    card = {
        "blocks": blocks
    }
    
    # If color is specified, add it using an attachment
    if color:
        card["attachments"] = [{
            "color": color
        }]
    
    return card


if __name__ == '__main__':
    """
    Main function to test the SlackMsg class
    This demonstrates how to use both send_msg and send_card methods
    """
    import argparse
    import socket
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test Slack message sending')
    parser.add_argument('-c', '--config', type=str, default='/etc/oqc/config2.toml',
                      help='Path to the configuration file')
    parser.add_argument('-r', '--robot_key', type=str, default='default',
                      help='The key name of the Slack robot defined in config')
    parser.add_argument('--slack_url', type=str, help='Slack webhook URL (overrides config)')
    parser.add_argument('--test_msg', action='store_true',
                      help='Test sending a simple message')
    parser.add_argument('--test_card', action='store_true',
                      help='Test sending a card message')
    
    args = parser.parse_args()
    
    try:
        # Create SlackMsg instance
        if not args.slack_url:
            print("Should specify a Slack URL via command line argument")
            exit(0)

            # Use the directly provided Slack URL
        logger.info("Using Slack URL provided via command line argument")
        slack = SlackMsg({args.robot_key: args.slack_url})
        
        # Send test message if requested
        if args.test_msg:
            test_message = f"This is a test message using SlackMsg.send_msg()"
            response = slack.send_msg(args.robot_key, test_message)
            logger.info(f"Slack message response: {response}")
        
        # Send test card if requested
        if args.test_card:
            card_title = f"Test Card "
            card_message = "This is a test message using SlackMsg.send_card()\nYou can include formatted text like *bold* and _italic_"
            card_body = create_basic_slack_card(card_title, card_message, color="#439FE0")
            
            response = slack.send_card(args.robot_key, card_body)
            logger.info(f"Slack card response: {response}")
        
        # If no specific test was requested, run both
        if not args.test_msg and not args.test_card:
            logger.info("Running both message and card tests as no specific test was requested")
            
            # Test simple message
            test_message = f"This is a test message using SlackMsg.send_msg()"
            logger.info(f"Sending test message to Slack robot '{args.robot_key}'")
            response = slack.send_msg(args.robot_key, test_message)
            logger.info(f"Slack message response: {response}")
            
            # Test card message
            card_title = f"Test Card"
            card_message = "This is a test message using SlackMsg.send_card()\nYou can include formatted text like *bold* and _italic_"
            card_body = create_basic_slack_card(card_title, card_message, color="#439FE0")
            
            logger.info(f"Sending test card to Slack robot '{args.robot_key}'")
            response = slack.send_card(args.robot_key, card_body)
            logger.info(f"Slack card response: {response}")
            
    except Exception as e:
        logger.error(f"Error during Slack test: {e}", exc_info=True)