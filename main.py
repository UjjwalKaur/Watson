import datetime
from dateutil import parser
import os.path
from dotenv import load_dotenv
import csv

from groq import Groq

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')
tasks_header = ["Task Name","Task Description","Department","Calendar","Start Datetime","End Datetime"]
now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
#today_day = now.strftime("%A")
#print(today_day)
tychr_calendar_id = '9516edcfcdd01aab1c8352e98a4816a4cbea47a5d41bf1360b615eecb985903a@group.calendar.google.com'
calendar_ids = {
  "Primary": "primary", 
  "Tychr" : "9516edcfcdd01aab1c8352e98a4816a4cbea47a5d41bf1360b615eecb985903a@group.calendar.google.com"
}

def main():
    content = organize_rant("""
                            
Here is a transcription of my rant: 
Schedule a meeting with Duvait at 3 pm and a meeting with Divya at 6 pm
                            """)
      
def get_rant():
    """Gets the users reponse through audio input or text"""
  
def get_prompt(rant):
    instructions = f"""
    You are a personal assistant that has to help plan, organize and schedule my tasks for me in the best way possible. YOUR MAIN OBJECTIVE IS TO DO WHAT IS IN MY BEST INTEREST AT ALL TIMES. TO PUSH ME TO ACHIEVE ALL MY GOALS AND TO CALL ME OUT WHEN I'M BEING LAZY AND TO REALLY MAKE SURE I WORK HARD. 
    BE HARD ON ME!
    For context, I have the following three jobs 
    I work as a Platform Manager at an EdTech Firm, called Tychr. They're launching a new Learning Management System and I am primarily responsible for its development and for ensuring all the content on the platform. 
    My responsibilities include:
    - Ensuring all the IB content on the platform for which I have to handle and set up meetings with the Content Developers
    - Ensuring the platform is being developed by the Tech team by providing constant feedback and creating timelines for them
    - Reach out to IB Alumni to hire them for the Buddies Project
    I also work as a Student Interviewer at Ladder Internships. I interview students and write up a brief summary of their interests to help match them with the right internships for them. 
    Additionally, I work as a Tutor. I currently have two students (Aastha Tharu and Avipasha) but I'm actively trying to find more students. 
    
    Moreover, I want to 10x every area of my life this year. These are my goals for 2025
    - Get well defined 11 line abs (Eat healthy and exercise 5 times a week)
    - 10x my income from 10,000 INR per month to 1,00,000 INR per month 
    - Invest 60,000 INR in the stock market
    - Become a Math/ Computer Science genius 
    - Reach 5,000 subscribers on Youtube
    - 10x your social capital - network
    - Create value in EdTech (ideally, start a startup)
    - Get into Stanford 
    
    I'm currently very actively working towards my Youtube goal of reaching 5,000 subscribers. I only have 34 right now so there's a long way to go. 
    
    Additionally, I'm also working for my non-profit, Saksharta, which helps students from under-resourced schools and colleges branch into Computer Science by working with experienced mentors on hands on projects. 
    For that, I need to reach out to students and professionals. 
    
    Because I have all this work, I am frustrated most of the time and hate planning out these little tasks that I need to carry out because I'm an extremely bad planner and I also hate my current job role at Tychr.
    
    Here are my personal preferences for scheduling events and working:
    - Always prioritize QUALITY over quantity. Set out separate days for DEEP WORK and separate days for MANAGEMENT/SMALLER TASKS
    - I realize the importance of efficiency and working smarter. Plan my days efficiently in the smartest ways possible. 
    - I like to use the EAT THE FROG technique - which means I like to do the hardest task first thing in the day. 
    - Afternoons are my downtime, I don't really like to do much in the afternoons especially between 3pm to 4:30 pm. 
    - Going 10x means I need to know where exactly to spend my time. I can't waste time on projects that yield very insiginificant results. I'm currently struggling with saying NO to things. I end up trying to juggle between so many activities and then being average at all of them.
    But because I'm going 10x this year, I can't afford to waste my time. I need to narrow down my scope. If you see me struggling through this, CALL ME OUT!
    
    For anything that needs to be scheduled, create a table with all the tasks I need to do listed as separate rows. Each row/task must have the following information:
    1. Task Name
    2. Task Description
    3. Department: [Tychr IB Buddy Project, Tech/ Design Team, Platform Content, Tychr Website, Personal Life, [The goal it corresponds to], Other [give a project area depending on the task]]
    4. Calendar: Tychr or Primary- Note that a Task belongs to the Tychr Calendar if it is work related to my role as a project manager at Tychr, in all other cases the task belongs to the primary calendar. Make sure there are no other options for this, either Tychr or Primary only
    5. Start Datetime in ISO 8601 format (timezone : India/Kolkata (+05:30)) (Choose a Time between now, {now} and 1 week from now unless otherwise stated by the user)
    6. End Datetime in ISO 8601 format (timezone : India/Kolkata (+05:30))
    Create this table in the .csv format with the csv code separated using ```csv and use exactly the mentioned column names as column headers. However, don't mention the headers inside the csv code.
    """
    prompt = f"""
    {rant}
    
    For context, these are all the tasks that are already scheduled.
    Existing Events = {get_events(calendar_ids['Primary']) + get_events(calendar_ids['Tychr'])}
    """
    return (instructions, prompt)
  
def organize_rant(rant):
    """Parse the rant and return an organized table with action items.
    eg. 
    Name of Task: 
    Department/Area: [Tychr IB Buddy Project, Tech/ Design Team, Platform Content, Tychr Website, Other]
    Calendar: [Tychr/primary]
    Action Classification: [Action 1: Schedule a Meeting, Action 2: Edit a Document, Action 3: Reach out/Follow up]
    Action Item: What needs to be done, project/task description, meeting description, agenda, what needs to be edited in detail
    """
    instructions, prompt = get_prompt(rant)

    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
          {"role" : "system", "content" : instructions},
          {"role" : "user", "content": prompt}
          ],
        temperature=1,
        max_completion_tokens=5024,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    content = ""
    for chunk in completion:
      content = content + (chunk.choices[0].delta.content or "")
    print(content)
    task_schedule = content.split('```csv')[1].split('```')[0]
    print(task_schedule)
    tasks = create_csv(task_schedule)
    schedule_blocks(tasks)
    return (content)

    
def authenticate_gcal():
    creds = None
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0, prompt="consent")
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())
    return creds
    
def get_events(calendarID):
    creds = authenticate_gcal()     
    try:
        service = build("calendar", "v3", credentials=creds)
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        events_result = (
            service.events()
            .list(
                calendarId=calendarID,
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
          return "All Free! No events exist!"

        # Prints the start and name of the next 10 events
        exisiting_events=""
        for event in events:
          start = event["start"].get("dateTime", event["start"].get("date"))
          start = parser.parse(start)
          end = event["end"].get("dateTime", event["end"].get("date"))
          end = parser.parse(end)
          exisiting_events = exisiting_events + f"{start} to {end} {event['summary']}\n"
        return exisiting_events

    except HttpError as error:
        print(f"An error occurred: {error}")
        
def create_csv(scheduled_tasks):
    with open('scheduled_tasks.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames = tasks_header)
        writer.writeheader()
        file.write(scheduled_tasks)
    tasks = []
    with open('scheduled_tasks.csv') as task_file:
        reader = csv.DictReader(task_file)
        print(reader)
        for row in reader:
          task = {
            "summary" : row["Task Name"],
            "calendarID" : calendar_ids[row["Calendar"]],
            "description" : row['Task Description'],
            "start" : {
                "dateTime": row["Start Datetime"],
                "timeZone": 'Asia/Kolkata',
            },
            "end" : {
              "dateTime" : row["End Datetime"],
              "timeZone" : 'Asia/Kolkata'
            }
            }
          tasks.append(task)
    return tasks
          
  
'''def segregate(updated_csv_file):
  """Iterate through the updated csv file and return a list of 3 separate dicts for each Action Type.

  Args:
      updated_csv_file (str): Updated schedule
  """
'''
  
def schedule_blocks(tasks):
  """Iterate through Action Items and schedule meetings one by one.

  Args:
      tasks (list): list containing all all Action 1 Items as dicts
  """
  creds = authenticate_gcal()
  try:
    service = build("calendar", "v3", credentials=creds) 
    for task in tasks:
      event = task.copy()
      event.pop('calendarID')
      event = service.events().insert(calendarId=task['calendarID'], body=event).execute()
      print('Event created: %s' % (event.get('htmlLink')))
  except HttpError as error:
    print(f"An error occurred: {error}")
  
if __name__ == '__main__':
    main()