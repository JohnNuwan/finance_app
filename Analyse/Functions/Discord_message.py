

import requests


# Webhook Partie Analyse
intra_webhook = "https://discord.com/api/webhooks/957910026478026772/8bkyJ2vuu2cmZONQBbI_iMUPJxjDd4yL8j9tubwxUhUkcDmpdeIhK11AXR5tOAPbLsPf"
daily_webhook = "https://discord.com/api/webhooks/957900372385599488/BWVc6gWhdvI917zKVNHIBEoDLMm4KuBoDtDymjIyTDAYvFo-B0Szmc1whAnxHCvKe-qp"

weekly_webhook = "https://discord.com/api/webhooks/957909951324508200/AYjWxJ41qJ-olkG6bmxc-OjZwMy3cAx5KFZcUu-iQC44rdcAx4SxnmMSrcaxHZktDjhg"

monthly_webhook = "https://discord.com/api/webhooks/957909853274263563/lDOH6sun6TTVGHP0vtVGYP64dnJ0dCuWe5gtTr0Vn1W2C4_97AysYz9EJSuuVE7taHKY"


Name = "Analyse Structure S/R & RSI"

Avatar = "https://i.imgur.com/F1UMx9K.jpeg"

def message_analyse(msg,channel):

	if channel == daily_webhook:
		try:
			# if a DISCORD URL is set in the config file, we will post to the discord webhook
			chat_message = {
					"username": Name,
					"avatar_url": Avatar,
					"content": f"------------------\n{msg}"
				}

			requests.post(daily_webhook, json=chat_message)
			
		except Exception as e:
			raise e

	if channel == weekly_webhook:
		try:
			# if a DISCORD URL is set in the config file, we will post to the discord webhook
			chat_message = {
					"username": Name,
					"avatar_url": Avatar,
					"content": f"------------------\n{msg}"
				}

			requests.post(weekly_webhook, json=chat_message)
			
		except Exception as e:
			raise e

	if channel == monthly_webhook:
		try:
			# if a DISCORD URL is set in the config file, we will post to the discord webhook
			chat_message = {
					"username": Name,
					"avatar_url": Avatar,
					"content": f"------------------\n{msg}"
				}

			requests.post(monthly_webhook, json=chat_message)
			
		except Exception as e:
			raise e

	if channel == intra_webhook:
		try:
			# if a DISCORD URL is set in the config file, we will post to the discord webhook
			chat_message = {
					"username": Name,
					"avatar_url": Avatar,
					"content": f"------------------\n{msg}"
				}

			requests.post(intra_webhook, json=chat_message)
			
		except Exception as e:
			raise e

