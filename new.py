import requests
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

# JSearch API endpoint and headers
url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": "",
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key="")

"""
# Function to retrieve job listings from JSearch API
def search_jobs(query):
    querystring = {"query": query, "page":"1","num_pages":"1"}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        if 'data' in data:
            return data['data']
        else:
            return []
    except requests.RequestException as e:
        print("Error fetching data from JSearch API:", e)
        return []
"""

def search_jobs(query, page=1, num_pages=3, date_posted="all", remote_jobs_only=False,
                employment_types=None, job_requirements=None, job_titles=None, company_types=None,
                employers=None, actively_hiring=False, radius=None, categories=None, country="us",
                language="en", exclude_job_publishers=None):

    querystring = {
        "query": query,
        "page": page,
        "num_pages": num_pages,
        "date_posted": date_posted,
        "remote_jobs_only": str(remote_jobs_only).lower(),
        "employment_types": employment_types,
        "job_requirements": job_requirements,
        "job_titles": job_titles,
        "company_types": company_types,
        "employers": employers,
        "actively_hiring": str(actively_hiring).lower(),
        "radius": radius,
        "categories": categories,
        "country": country,
        "language": language,
        "exclude_job_publishers": exclude_job_publishers
    }

    # Remove None values from querystring
    querystring = {k: v for k, v in querystring.items() if v is not None}
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# OPENAI ASSISTANT DEFINITION #####################################

def create_thread():
    thread = client.beta.threads.create()
    return thread.id

def start(thread_id , prompt):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

def get_response(thread_id, assistant_id):
    
    run = client.beta.threads.runs.create(
      thread_id=thread_id,
      assistant_id=assistant_id,
      instructions="Answer user questions using custom functions available to you."
    )
    
    # Wait for the run to complete
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    while run_status.status != "completed":
        
        if run_status.status == 'requires_action':
            
            def get_outputs_for_tool_call(tool_call):
                if tool_call.function.name == "search_jobs":
                    query = json.loads(tool_call.function.arguments)["query"] 
                    date_posted = json.loads(tool_call.function.arguments)["date_posted"]
                    employment_type = json.loads(tool_call.function.arguments).get("employment_type")
                    job_requirements= json.loads(tool_call.function.arguments).get("job_requirements")
                    actively_hiring=json.loads(tool_call.function.arguments).get("actively_hiring")
                    output = search_jobs(query) 
                    output_str = json.dumps(output)
                    output_str = output_str[:512 * 1024]
                return {
                    "tool_call_id":tool_call.id,
                    "output":output_str
                }
               
            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
            tool_outputs = map(get_outputs_for_tool_call, tool_calls)
            tool_outputs = list(tool_outputs)

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        time.sleep(1)
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Retrieve the latest message from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    return response

# Example usage
prompt = "Find the recent Management jobs in the Manufacturing company type and segregate them on the basis of onsite and online with the help of their job desctiption , give only the final count to me, i dont need the job descriptions or jobs, i just need the numerical analysis."

assistant_id = "asst_wj2NcJDmpxQ1mWiMcnCcL2Li"
thread_id = create_thread()
start(thread_id,prompt)
#thread_id = "thread_oWVUlvrYVJitWFoP6w59FtQ"

response = get_response(thread_id,assistant_id)
#result = search_jobs(prompt)
print(response)



