import discord
import random
import asyncio
import openai
import os

# Set your OpenAI API key here (ensure it's stored securely, not directly in the code)
openai.api_key = os.getenv('sk')
class GenshinQuizBot(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.questions = [
            {"question": "What is the name of the main character in Genshin Impact?", "options": ["Aether", "Lumine", "Zhongli", "Venti"], "answer": "Aether"},
            {"question": "Which element does the character Diluc have?", "options": ["Pyro", "Cryo", "Hydro", "Geo"], "answer": "Pyro"},
            {"question": "What is the name of the city in Mondstadt?", "options": ["Liyue", "Mondstadt", "Inazuma", "Sumeru"], "answer": "Mondstadt"},
            {"question": "Who is the Electro Archon in Inazuma?", "options": ["Raiden Shogun", "Kamisato Ayaka", "Beidou", "Lisa"], "answer": "Raiden Shogun"},
            {"question": "What is the highest rarity of characters in Genshin Impact?", "options": ["4 stars", "5 stars", "6 stars", "3 stars"], "answer": "5 stars"},
            {"question": "Which character is known as the 'Vigilant Yaksha'?", "options": ["Zhongli", "Chongyun", "Xiao", "Tartaglia"], "answer": "Xiao"},
            {"question": "Which element is associated with the character Mona?", "options": ["Hydro", "Pyro", "Anemo", "Geo"], "answer": "Hydro"}
        ]
        self.current_question = None
        self.scores = {}
        self.quiz_active = False
        self.rounds_played = 0
        self.max_rounds = 5

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Genshin Quiz Commands
        if message.content.lower() == "$startquiz":
            await self.start_quiz(message)

        elif message.content.lower().startswith("$answer"):
            await self.check_answer(message)

        elif message.content.lower() == "$endquiz":
            await self.end_quiz(message)

        elif message.content.lower() == "$leaderboard":
            await self.show_leaderboard(message)

        # GPT Chat Commands
        elif message.content.lower() == "$startchat":
            await message.channel.send("Hi! I am your friendly bot. You can start chatting with me!")
        
        elif message.content.lower() == "$endchat":
            await message.channel.send("Goodbye! Type `$startchat` to talk to me again.")
        
        else:
            response = await self.chat_with_gpt(message.content)
            await message.channel.send(response)

    async def start_quiz(self, message):
        if self.quiz_active:
            await message.channel.send("A quiz is already active! Type `$endquiz` to end the current quiz and start a new one.")
            return

        self.scores = {}
        self.rounds_played = 0
        self.quiz_active = True
        await self.ask_question(message)

    async def ask_question(self, message):
        if self.rounds_played >= self.max_rounds:
            await message.channel.send("The quiz is over! Type `$endquiz` to see the final scores.")
            return
        
        self.current_question = random.choice(self.questions)
        options = "\n".join([f"{index+1}. {option}" for index, option in enumerate(self.current_question["options"])])
        await message.channel.send(f"Question {self.rounds_played + 1}: {self.current_question['question']}\nOptions:\n{options}\n\nYou have 30 seconds to answer. Type your answer using `$answer [Option Number]`.")
        await asyncio.sleep(30)

        if self.current_question:
            await message.channel.send(f"Time's up! The correct answer was: {self.current_question['answer']}.")
            self.current_question = None
            if self.quiz_active:
                self.rounds_played += 1
                await self.ask_question(message)

    async def check_answer(self, message):
        if not self.current_question:
            await message.channel.send("No active quiz. Type `$startquiz` to begin a new quiz.")
            return

        answer_given = message.content.split(" ")[1]
        correct_answer = self.current_question["answer"]

        if self.current_question["options"][int(answer_given) - 1] == correct_answer:
            if message.author.id not in self.scores:
                self.scores[message.author.id] = 0
            self.scores[message.author.id] += 1
            await message.channel.send(f"Correct, {message.author.mention}! 🎉 Your score: {self.scores[message.author.id]}")
        else:
            if message.author.id not in self.scores:
                self.scores[message.author.id] = 0
            await message.channel.send(f"Sorry, {message.author.mention}. The correct answer was: {correct_answer}. Your score: {self.scores[message.author.id]}")

        self.current_question = None

        if self.quiz_active:
            self.rounds_played += 1
            await self.ask_question(message)

    async def end_quiz(self, message):
        if not self.quiz_active:
            await message.channel.send("No quiz is currently active.")
            return

        self.quiz_active = False
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = "\n".join([f"<@{user_id}>: {score}" for user_id, score in sorted_scores])
        await message.channel.send(f"The quiz has ended! Here's the final leaderboard:\n{leaderboard}")

    async def show_leaderboard(self, message):
        if not self.scores:
            await message.channel.send("No scores available. Start a quiz first with `$startquiz`.")
            return

        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = "\n".join([f"<@{user_id}>: {score}" for user_id, score in sorted_scores])
        await message.channel.send(f"Current leaderboard:\n{leaderboard}")

    async def chat_with_gpt(self, user_message):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" depending on your choice
                messages=[{"role": "user", "content": user_message}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error communicating with GPT: {e}")
            return f"Sorry, something went wrong. Error: {e}"

# Create intents for reading message content
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content

# Create and run the bot
client = GenshinQuizBot(intents=intents)
client.run('MTMzMDE5NDA5NzQ3ODE3Njk1OQ.G6omSP.kJMlqsZkHlxPwFe_TWZ4DOgAp67pZAZ57fytgQ')  # Insert your Discord Bot Token here
