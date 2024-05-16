---
title: NotionGPT
emoji: 🚀
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.29.0
app_file: gradio_app.py
pinned: false
---

# Quickstart Guide

## Notion API

### Creating your integration in Notion

1. Go to [Notion's My Integrations page](https://www.notion.so/my-integrations).
2. Click `+ New Integration`.
3. Enter the integration name. (NotionGPT is a good choice)

### Get your API key

1. Click on the integration you created.
2. Visit the `Secrets` tab.
3. Copy the `Internal Integration Secret` and save it for later.

### Give your integration page permissions

1. Create the page where NotionGPT will store all the generated content. (We named ours NotionGPT Generator)
2. Get the page ID by copying the last series of characters in the URL. (e.g. `https://www.notion.so/NotionGPT-Generator-<PAGE_ID>`)
3. Click on the `...` more menu in the top-right corner of the page.
4. Scroll down to connections and click `Connect to`.
5. Search for the integration you created, click it, and select `Confirm`.

## OpenAI API

### Setting up your account
1. Create an account on [OpenAI](https://platform.openai.com/signup) or log in if you already have one.
2. Visit the [Billings page](https://platform.openai.com/settings/organization/billing/overview) and add a payment method to your account.
3. Click `Add to credit balance` and add some funds to your account, we recommend $10 to start.

### Get your API key

1. Go to the [API keys page](https://platform.openai.com/account/api-keys). (Note that you may have to verify your phone number to do so)
2. Click `+ Create new secret key`, and name it. (NotionGPT is a good choice)
3. Copy the key and save it for later, you won't be able to see it again.

### Finetuning the GPT model

1. Download `data/finetuning_data_cot_v8.jsonl` in the GitHub repository.
2. Visit the [OpenAI Fine-tuning page](https://platform.openai.com/finetune) and click `+ Create` in the top right corner.
3. Fill in the form with the following information, and leave the rest as default:
   - `Base Model`: `gpt-3.5-turbo-0125` (or any other model you prefer)
   - `Training data`: Upload the `finetuning_data_cot_v8.jsonl` file.
   - `Suffix`: NotionGPT (or any other name you prefer)
4. Click `Create` and wait for the model to finish training.
5. Once the model is trained, copy the model name and save it for later. (It should look something like `ft:gpt-3.5-turbo-0125:personal:notiongpt:<ID>`)

## Unsplash API

### Get your API key

1. Create an account on [Unsplash](https://unsplash.com/join) or log in if you already have one.
2. Go to [Unsplash's Applications page](https://unsplash.com/oauth/applications).
3. Click `New Application`.
4. Agree to all the terms and condtions and click `Accept terms`.
5. Fill in your application name and description. (NotionGPT is a good choice for both)
6. Click `Create application`.
7. Scroll down to keys and copy the `Access Key` and save it for later.

## Setting up the app

### Hugging Face Spaces

1. Create an account on [Hugging Face](https://huggingface.co/join) or log in if you already have one.
2. Visit the NotionGPT space [here](https://huggingface.co/spaces/sbhatti2009/NotionGPT).
3. Click on the `...` more menu in the top-right corner of the space.
4. Select `Duplicate this space`.
5. Keep everything the same, but set your `Space secrets` according to the information below:
   - `UNSPLASH_ACCESS_KEY`: Your Unsplash API key.
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `NOTION_KEY`: Your Notion API key.
   - `NOTION_PAGE_ID`: The page ID of the page you created in Notion.
   - `NOTION_GPT_MODEL_NAME`: The name of the fine-tuned model.
6. Click `Duplicate Space`, and wait for the application to build. (Note that this may take a few minutes)
7. Enjoy using NotionGPT! 🎉