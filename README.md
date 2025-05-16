# LiveKit Voice Agent Form Filler

This repo contains both a NextJS frontend and a LiveKit Agents backend.
You can speak with the voice agent to fill out the form items.
You can manually enter the form items and the agent will get those values.
You can tell the agent to submit the form for you.

## Getting started

1. Set up the frontend environment by copying `.env.example` to `.env.local` and fill in the required values.
2. Then, set up the agent environment in the agent directory by copying `.env.example` to `.env` and fill in the required values there.

Then run the frontend app:

```bash
yarn install
yarn dev
```

And open http://localhost:3000 in your browser.

You'll also need the agent to speak with.
In a separate terminal, in the agent directory, run the following:

```console
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py download-files
```
