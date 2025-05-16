# LiveKit Voice Agent Form Filler

## Getting started

1. Set up the frontend environment by copying `.env.example` to `.env.local` and fill in the required values.
2. Then, set up the agent environment in the agent directory by copying `.env.example` to `.env` and fill in the required values there.

Then run the the frontend app:

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
