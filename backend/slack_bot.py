import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from engine import answer

app = App(token=os.environ['SLACK_BOT_TOKEN'])

@app.event('app_mention')
def mention(event,say):
    question=event.get('text','').split('>',1)[-1].strip()
    if not question:
        say('Mention me with a company policy question.',thread_ts=event.get('ts'))
        return
    try:
        res=answer(question,'llm_vector')
        say(f"*Answer:* {res['answer']}\n*Relevant policy:* {res['policy']}",thread_ts=event.get('ts'))
    except Exception as e:
        say(f'Could not look up the policy. Check the local model setup. Error: {e}',thread_ts=event.get('ts'))

if __name__=='__main__':
    SocketModeHandler(app,os.environ['SLACK_APP_TOKEN']).start()
