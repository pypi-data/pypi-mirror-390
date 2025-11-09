from twilio.rest import Client

def get_twilio_client(clientidsecret: str) -> Client:
    client_id, client_secret = clientidsecret.split(':')
    return Client(client_id, client_secret)