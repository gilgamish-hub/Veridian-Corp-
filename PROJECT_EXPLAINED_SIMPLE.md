# 🎈 Veridian IT Helper — Simply Explained

Welcome! If you're looking at the app on your screen and wondering **"What is this, how does it work, and why did we build it?"** — this guide is written just for you, in simple, everyday language. No coding words!

---

## 1. 💡 What Did We Build?

Imagine you work at a big company called **Veridian Corp**. 

Every day, hundreds of employees have IT problems:
- *"I got locked out of my computer!"*
- *"My laptop is old and broken, can I get a new one?"*
- *"I received a weird email, is it a virus?"*
- *"A visitor needs Wi-Fi access today."*

Usually, human IT staff have to read every single email, check the company rules, and decide what to do. This takes a lot of time.

**What we built:**
We built an **Automated Smart IT Helper**. It acts like a super-fast, 24/7 digital IT receptionist that reads employee requests, checks the official company rulebook, makes the right decision instantly, and performs the fix automatically whenever allowed.

---

## 2. 🧠 Why Is This Special? (The "No-Guessing" Rule)

Normal AI chatbots sometimes make things up or guess when they don't know the answer. In a company, that is dangerous! (Imagine an AI giving away free expensive laptops by mistake).

Our system follows a **Strict Rulebook Strategy**:
- It reads company policies (like *"Laptops can only be replaced if they are older than 3 years"*).
- It checks exact facts (like *"Is Aditi's laptop 3.5 years old? Yes!"*).
- It follows the rulebook **100% strictly without guessing**.

---

## 3. ⚙️ How Does It Work Behind the Scenes? (The 5 Simple Steps)

Whenever an employee sends a message, our digital helper processes it in **5 simple steps**:

```
[Employee Message] 
        ⬇️
Step 1: Understand the Problem (What is the issue?)
        ⬇️
Step 2: Read the Rulebook (What is the company policy for this?)
        ⬇️
Step 3: Make the Decision (Approve, Fix Automatically, Pass to Human, or Ask Question)
        ⬇️
Step 4: Take Action (Unlock account, send replacement request, or alert security)
        ⬇️
Step 5: Write the Reply (Send a clear, friendly answer to the employee)
```

Here is what happens in each step:

### Step 1: Understand the Problem
The helper reads the message and identifies:
- Who is asking? (Full-time employee or temporary contractor?)
- What is broken? (Password, Laptop, Wi-Fi, Printer, or Email?)
- Important numbers (e.g., laptop age = 3.5 years, failed logins = 6 times).

### Step 2: Read the Rulebook
It searches the company Knowledge Base to find the exact rule that applies:
- Rule KB-01 for passwords
- Rule KB-03 for laptops
- Rule KB-07 for visitor Wi-Fi
- Rule KB-09 for phishing/scams

### Step 3: Make the Decision
Based on the rulebook, it picks one of **4 outcomes**:
1. **FIX AUTOMATICALLY (Resolve)** — e.g. Unlock password instantly.
2. **APPROVE** — e.g. Order a new laptop because the old one is 3.5 years old.
3. **PASS TO HUMAN (Route)** — e.g. Send a suspicious email to the Security Team.
4. **ASK FOR DETAILS (Clarify)** — e.g. If the message just says *"help, it's not working"*, ask what isn't working.

### Step 4: Take Action
The helper presses the button to do the real work! It actually unlocks the account, sends the replacement order to the warehouse, or sends a red alert to security.

### Step 5: Write the Reply
It sends a polite, clear message back to the employee explaining what was done and why.

---

## 4. 📋 Real Examples of What We Tested

Here are 4 simple examples of what our helper handles on your screen:

| Employee | What They Asked | What the Helper Did | Why? |
| :--- | :--- | :--- | :--- |
| **Karan Mehta** | *"I entered password wrong 6 times and got locked out."* | **Unlocked account automatically** | Rule KB-01 allows automatic unlock after 5 failed tries. |
| **Aditi Sharma** | *"My laptop screen is dead and it is 3.5 years old."* | **Approved new laptop order** | Rule KB-03 says laptops older than 3 years can be replaced. |
| **Vikram Chawla**| *"A visitor needs Wi-Fi tomorrow."* | **Gave self-service instructions** | Rule KB-07 says guests can get 24-hr passes at the lobby kiosk. |
| **Ananya Reddy**| *"I got a weird email asking for password so I forwarded it to my team."* | **Alerted Security & warned employee** | Rule KB-09 says NEVER forward phishing emails; alert security immediately. |

---

## 5. 🖥️ How to Use the Screen You Have Open Right Now

On the website open in your browser (`http://localhost:8501`):

1. **Left Side (Select Request):**
   - Click the dropdown menu.
   - Pick any test employee from `REQ-01` to `REQ-15`.
   - You will see their name, job role, and what issue they wrote.

2. **Red Button ("Run Agent Pipeline"):**
   - Click this button!
   - Watch the right side instantly show you:
     - **Result Overview**: The final decision (APPROVED, RESOLVED, ROUTED).
     - **Node 1 to 5**: Each of the 5 steps happening in real-time.
     - **Final Response**: The exact friendly message sent to the employee.

3. **Try Custom Request Tab:**
   - Click the middle tab at the top (*"✏️ Custom Request Tester"*).
   - Type in any request you want (e.g., *"I work from home 4 days a week and need a monitor"*) and hit **Submit** to see how the helper handles it!

---

### 🌟 Summary
You now have a complete, intelligent IT support system that automatically handles employee requests according to company policy, saves hundreds of hours for human IT staff, and never makes unauthorized decisions!
