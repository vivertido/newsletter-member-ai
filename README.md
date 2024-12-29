# AI Membership Assistant

This is a Streamlit-based application designed to assist with managing Mailchimp subscriber lists, analyzing click activity on Wordpress posts via the newsletter, and generating personalized fundraising emails based on member click behavior.

It is a work in progress built at Cityside Journalism for the goal of prototyping a solution to obtain more revenue from Mailchimp newsletter subscribers. 

## Core functionality
Sync newsletter audience members and generate emails based on their headline click activity on newsletters linked to Wordpress posts.

## Features

- **Authentication**: Secure login to access the application.
- **Newsletter Management**: Add and view newsletters, sync subscribers from Mailchimp.
- **Click Activity Analysis**: Fetch and analyze click activity from newsletters.
- **AI Click Analyzer**: Generate personalized marketing emails based on member click activity using OpenAI.
- **Member Data**: Fetch and display subscriber data based on various criteria.

## Prereqs
- Mailchimp subscribers lists and campaigns to fetch.
- A live Wordpress site with active posts inlcuded in the newsletters.
- A valid Mailchip API key
- A Supabase account and API key
- A valid OpenAI API key (for generating emails)
  
## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/membership-helper.git
    cd membership-helper
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up Streamlit secrets:
    - Create a [secrets.toml](http://_vscodecontentref_/18) file in the `.streamlit` directory with the following content:
    ```toml
    [auth]
    username = "your_username"
    password = "your_password"

    API_KEY = "your_mailchimp_api_key"
    MC_KEY = "your_mailchimp_marketing_key"
    OPEN_AI_KEY = "your_openai_api_key"
    SB_URL = "your_supabase_url"
    SB_KEY = "your_supabase_key"
    ```

# Usage

1. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

2. Open your web browser and navigate to `http://localhost:8080`.

## File Descriptions

- **app.py**: Main entry point of the application.
- **chimp/**: Contains modules for interacting with Mailchimp.
  - [member_clicks.py](http://_vscodecontentref_/19): Fetches member activity from Mailchimp.
  - [newsletters.py](http://_vscodecontentref_/20): Manages newsletters and subscribers.
  - [subscriber_sync.py](http://_vscodecontentref_/21): Syncs subscribers from Mailchimp.
- **pages/**: Contains Streamlit pages for different functionalities.
  - [ai_click_analyzer.py](http://_vscodecontentref_/22): Generates personalized marketing emails.
  - [click_activity.py](http://_vscodecontentref_/23): Analyzes click activity from newsletters.
  - [login.py](http://_vscodecontentref_/24): Handles user authentication.
  - [manage_newsletters.py](http://_vscodecontentref_/25): Manages newsletters.
  - [member_data.py](http://_vscodecontentref_/26): Displays subscriber data.
- **prompts/**: Contains prompt templates for generating emails.
  - [test_gen_funraising.py](http://_vscodecontentref_/27): Templates for fundraising emails.
- **db.py**: Contains database interaction logic using Supabase.
- **email_generator.py**: Generates personalized emails using OpenAI.
- **tasks.py**: Contains background tasks for processing click activity.
- **utils.py**: Utility functions for URL parsing and data cleaning.
- **requirements.txt**: Lists the required Python packages.
- **README.md**: This file.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
    
