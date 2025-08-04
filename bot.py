"""
This bot will not work if you run as it is, the format of file structure required is changed for the purpose of this repository.
Please edit the paths before running it(if you want to).

Bot Credits: Anirudh Gupta and Agrim Arsh
"""

import asyncio
import datetime
import json
import os
import traceback
from typing import Any, Dict, Literal, Optional

import discord
import regex
from discord import Embed, app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
TREE = bot.tree

DATA_FILE = "data.json"
FLAGS_FILE = "flags.json"
ORDER_FILE = "problem_order.json"
PROBLEMS_FOLDER = "Problems"
ATTACHMENTS_FOLDER = "Attachments"

PROBLEM_POINTS = 20
FRENZY_POINTS = 5

# Ensure directories exist
os.makedirs(PROBLEMS_FOLDER, exist_ok=True)
os.makedirs(ATTACHMENTS_FOLDER, exist_ok=True)

initial_json = {"teams": {}, "leaderboard_channel": None, "started": False, "paused" : True}

# Initialize files
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump(initial_json, f)

if not os.path.exists(FLAGS_FILE):
    with open(FLAGS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(ORDER_FILE):
    with open(ORDER_FILE, "w") as f:
        json.dump({"order": []}, f)

def load_data() -> Dict[str, Any]:
    """Load data from file with error handling"""
    try:
        if not os.path.exists(DATA_FILE):
            return initial_json
            
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        # Validate data structure
        if not all(key in data for key in ["teams", "leaderboard_channel", "started"]):
            raise ValueError("Invalid data structure")
            
        return data
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading data file: {str(e)}")
        return initial_json

def save_data(data: Dict[str, Any]) -> None:
    """Save data to file with error handling"""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving data file: {str(e)}")

def load_flags() -> Dict[str, Any]:
    """Load flags from file with error handling"""
    try:
        if not os.path.exists(FLAGS_FILE):
            return {}
            
        with open(FLAGS_FILE, "r") as f:
            flags = json.load(f)
            
        return flags

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading flags file: {str(e)}")
        return {}

def save_flags(flags: Dict[str, Any]) -> None:
    """Save flags to file with error handling"""
    try:
        with open(FLAGS_FILE, "w") as f:
            json.dump(flags, f, indent=2)
    except IOError as e:
        print(f"Error saving flags file: {str(e)}")

def load_problem_order() -> Dict[str, Any]:
    """Load problem order from file"""
    try:
        if not os.path.exists(ORDER_FILE):
            return {"order": []}
            
        with open(ORDER_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading problem order: {str(e)}")
        return {"order": []}

def save_problem_order(order_data: Dict[str, Any]) -> None:
    """Save problem order to file"""
    try:
        with open(ORDER_FILE, "w") as f:
            json.dump(order_data, f, indent=2)
    except IOError as e:
        print(f"Error saving problem order: {str(e)}")

def get_problem_number(problem_name: str) -> Optional[int]:
    """Get the order number for a problem name"""
    order_data = load_problem_order()
    try:
        return order_data["order"].index(problem_name) + 1
    except ValueError:
        return None

def get_next_problem_name(current_problem_name: str) -> Optional[str]:
    """Get the name of the next problem in sequence"""
    order_data = load_problem_order()
    try:
        current_index = order_data["order"].index(current_problem_name)
        if current_index + 1 < len(order_data["order"]):
            return order_data["order"][current_index + 1]
    except ValueError:
        pass
    return None

def is_admin_channel():
    """Check if the command is being run in an admin-only channel"""
    def predicate(interaction: discord.Interaction) -> bool:
        # Define allowed admin channels (e.g., "admin-commands")
        ADMIN_CHANNELS = ["sandbix", "admin-general", "functions", "problem_hints"]
        
        # Allowance in DMs (optional)
        if not interaction.guild:
            return False
        
        # Check if channel is allowed
        return interaction.channel.name in ADMIN_CHANNELS or "admin" in interaction.channel.name
    
    return app_commands.check(predicate)

async def send_problem(channel: discord.TextChannel, problem_data: Dict[str, Any], problem_name: str, team_name: str) -> bool:
    """Send a complete problem with description and attachments to a channel (text-only version)"""
    try:
        problem_path = os.path.join(PROBLEMS_FOLDER, problem_data["problem"])
        if not os.path.exists(problem_path):
            print(f"Problem file not found: {problem_path}")
            return False
        
        # Read and parse problem content
        with open(problem_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        lines = content.split('\n')
        title = problem_name 
        description = '\n'.join(lines).strip()
        
        # Send the problem header
        await channel.send(
            f"**🆕 PROBLEM: {title}**\n"
            f"**Problem Number:** {get_problem_number(problem_name)}\n"
            f"**Points:** {problem_data['points']} | "
            f"**Created By:** {problem_data.get('author', 'Databased Team')}\n"
            f"**Team:** {team_name}\n"
            f"Submit flags with `/submit [flag]`\n"
            "────────────────────"
        )
         
        # Handle attachments if they exist
        if "attachments" in problem_data and problem_data["attachments"]:
            await channel.send("\n**📎 PROBLEM ATTACHMENT(S):**")
            
            for attachment in problem_data["attachments"]:
                if "path" in attachment:  # Local file
                    file_path = os.path.join(attachment["path"])
                    if os.path.exists(file_path):
                        try:
                            # Send file with description
                            file_msg = f"📁 **{os.path.basename(file_path)}**"
                            if attachment.get("type"):
                                file_msg += f" ({attachment['type']})"
                            
                            await channel.send(
                                content=file_msg,
                                file=discord.File(file_path)
                                )

                            await channel.send("────────────────────\n")
                        except Exception as e:
                            print(f"Failed to send attachment {file_path}: {str(e)}")
                            await channel.send(f"⚠️ Could not send attachment: {os.path.basename(file_path)}")
                    else:
                        print(f"Attachment not found: {file_path}")
                        await channel.send(f"⚠️ Missing attachment: {os.path.basename(file_path)}")
                
                elif "url" in attachment:  # Public URL
                    url_msg = f"🔗 **Attachment URL:** {attachment['url']}"
                    if attachment.get("type"):
                        url_msg += f" ({attachment['type']})"
                    await channel.send(url_msg)

        # Send the problem description (split if too long)
        description_msg = f"**📋 Problem Description:**\n\n{description}"
        if len(description_msg) <= 2000:
            await channel.send(description_msg)
        else:
            # Split description into chunks of ~1950 characters to leave room for formatting
            chunks = []
            current_chunk = ""
            lines = description.split('\n')
            
            for line in lines:
                if len(current_chunk) + len(line) + 1 <= 1950:  # +1 for newline
                    current_chunk += line + '\n' if current_chunk else line
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = line
            
            if current_chunk:
                chunks.append(current_chunk)
            
            # Send each chunk
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await channel.send(chunk)
                else:
                    await channel.send(f"{chunk}")
        
        return True
        
    except Exception as e:
        print(f"Error sending problem: {str(e)}")
        traceback.print_exc()
        await channel.send("❌ An error occurred while displaying this problem. Please notify an admin.")
        return False

async def update_leaderboard(interaction: discord.Interaction, data: Dict[str, Any]) -> None:
    """Update the leaderboard channel"""
    if not data.get("leaderboard_channel"):
        return
        
    channel = interaction.guild.get_channel(data["leaderboard_channel"])
    if not channel:
        return

    try:
        # Separate teams by category
        fresher_teams = []
        senior_teams = []
        
        for team, info in data["teams"].items():
            if info.get("category") == "fresher":
                fresher_teams.append((team, info))
            else:
                senior_teams.append((team, info))
        
        # Sort each category by score (descending)
        fresher_teams.sort(key=lambda x: -x[1]["score"])
        senior_teams.sort(key=lambda x: -x[1]["score"])
        
        embed = Embed(
            title="📊 Current Leaderboard",
            color=discord.Color.gold()
        )
        
        # Add fresher teams (top 10)
        if fresher_teams:
            fresher_text = ""
            for i, (team, info) in enumerate(fresher_teams[:10], 1):
                current_problem = info["current_problem"]
                problem_num = get_problem_number(current_problem) if current_problem else "N/A"
                fresher_text += f"{i}. **{team}** - {info['score']} pts\n"
            
            embed.add_field(
                name="🥇 FRESHER TEAMS (Top 10)",
                value=fresher_text or "No fresher teams",
                inline=False
            )
        
        # Add senior teams (top 10)
        if senior_teams:
            senior_text = ""
            for i, (team, info) in enumerate(senior_teams[:10], 1):
                current_problem = info["current_problem"]
                problem_num = get_problem_number(current_problem) if current_problem else "N/A"
                senior_text += f"{i}. **{team}** - {info['score']} pts\n"
            
            embed.add_field(
                name="🏆 SENIOR TEAMS (Top 10)",
                value=senior_text or "No senior teams",
                inline=False
            )
        
        # Try to find previous leaderboard message to edit
        async for message in channel.history(limit=10):
            if message.author == bot.user and message.embeds and "Leaderboard" in message.embeds[0].title:
                await message.edit(embed=embed)
                return

        # If no existing message found, send new one
        await channel.send(embed=embed)
        
    except discord.HTTPException as e:
        print(f"Failed to update leaderboard: {str(e)}")

@bot.event
async def on_ready():
    await TREE.sync()
    print(f"Bot is ready. Logged in as {bot.user}")

def is_admin():
    def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command. (Admin only)", 
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandInvokeError):
        await interaction.response.send_message(
            "⚠️ An unexpected error occurred while executing the command. The admins have been notified.", 
            ephemeral=True
        )
        print(f"Command error: {error.original}")
        traceback.print_exc()
    else:
        await interaction.response.send_message(
            "⚠️ Something went wrong with the bot. Please contact the bot administrators.", 
            ephemeral=True
        )
        print(f"Unexpected error: {error}")
        traceback.print_exc()

@TREE.command(name="set_leaderboard", description="Set the Leaderboard Channel")
@is_admin()
@is_admin_channel()
async def set_leaderboard_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    data = load_data()
    data["leaderboard_channel"] = channel.id
    save_data(data)
    content = "🏁Leaderboard channel set! We are good to go!"
    await channel.send(content)
    await interaction.response.send_message(content)

@TREE.command(name="add_problem", description="Add a new problem with attachments (admin only)")
@is_admin()
@is_admin_channel()
async def add_problem(
    interaction: discord.Interaction,
    problem_name: str,
    author: str,
    problem_file: discord.Attachment,
    flag: str,
    points: int = PROBLEM_POINTS,
    insert_after: Optional[str] = None,
    attachment1: Optional[discord.Attachment] = None,
    attachment2: Optional[discord.Attachment] = None,
    attachment3: Optional[discord.Attachment] = None
):
    """Add a new problem with optional file attachments"""
    await interaction.response.defer(ephemeral=True)
    
    # Validate problem name
    problem_name = problem_name.strip().replace(" ", "_")
    if not problem_name:
        await interaction.followup.send("❌ Problem name cannot be empty!", ephemeral=True)
        return
    
    flags = load_flags()
    if problem_name in flags:
        await interaction.followup.send(f"❌ Problem '{problem_name}' already exists!", ephemeral=True)
        return

    # Save problem file
    problem_filename = f"{problem_name}.md"
    problem_path = os.path.join(PROBLEMS_FOLDER, problem_filename)
    
    try:
        await problem_file.save(problem_path)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to save problem file: {str(e)}", ephemeral=True)
        return

    # Process attachments
    problem_attachments = []
    attachments = [a for a in [attachment1, attachment2, attachment3] if a is not None]
    
    for attachment in attachments:
        try:
            # Save each attachment
            attachment_filename = f"{problem_name}_{attachment.filename}"
            attachment_path = os.path.join(ATTACHMENTS_FOLDER, attachment_filename)
            await attachment.save(attachment_path)
            
            # Determine attachment type based on file extension
            file_ext = os.path.splitext(attachment.filename)[1].lower()
            attachment_type = "image" if file_ext in ['.png', '.jpg', '.jpeg', '.gif'] else "file"
            
            problem_attachments.append({
                "type": attachment_type,
                "path": attachment_path
            })
        except Exception as e:
            print(f"Failed to save attachment {attachment.filename}: {str(e)}")
            continue

    # Add to flags
    flags[problem_name] = {
        "problem": problem_filename,
        "flag": flag.strip(),
        "author": author.strip(),
        "points": points,
        "attachments": problem_attachments,
        "first_access": None,
    }
    
    # Add to problem order
    order_data = load_problem_order()
    if insert_after:
        try:
            index = order_data["order"].index(insert_after) + 1
            order_data["order"].insert(index, problem_name)
        except ValueError:
            await interaction.followup.send(f"❌ Problem '{insert_after}' not found in order list. Added to end.", ephemeral=True)
            order_data["order"].append(problem_name)
    else:
        order_data["order"].append(problem_name)
    
    save_flags(flags)
    save_problem_order(order_data)
    
    response = (
        f"✅ Problem '{problem_name}' added successfully!\n"
        f"Position: {order_data['order'].index(problem_name) + 1}\n"
        f"Flag: ||{flag}||\n"
        f"Points: {points}\n"
        f"Author: {author}\n"
    )

    if problem_attachments:
        response += f"\nAttachments saved: {len(problem_attachments)}"
    
    await interaction.followup.send(response, ephemeral=True)

@TREE.command(name="add_attachment", description="Add an attachment to a problem (admin only)")
@is_admin()
@is_admin_channel()
async def add_attachment(
    interaction: discord.Interaction,
    problem_name: str,
    attachment: discord.Attachment,
    attachment_type: Optional[str] = None
):
    """Add an attachment to an existing problem"""
    await interaction.response.defer(ephemeral=True)
    
    flags = load_flags()
    if problem_name not in flags:
        await interaction.followup.send(f"❌ Problem '{problem_name}' doesn't exist!", ephemeral=True)
        return
    
    # Determine attachment type if not specified
    if attachment_type is None:
        file_ext = os.path.splitext(attachment.filename)[1].lower()
        attachment_type = "image" if file_ext in ['.png', '.jpg', '.jpeg', '.gif'] else "file"
    
    # Save file locally
    filename = f"{problem_name}_{attachment.filename}"
    filepath = os.path.join(ATTACHMENTS_FOLDER, filename)
    
    try:
        await attachment.save(filepath)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to save attachment: {str(e)}", ephemeral=True)
        return

    # Update problem data
    if "attachments" not in flags[problem_name]:
        flags[problem_name]["attachments"] = []
    
    flags[problem_name]["attachments"].append({
        "type": attachment_type,
        "path": filepath
    })
    
    save_flags(flags)
    await interaction.followup.send(
        f"✅ Attachment added to Problem '{problem_name}'!\n"
        f"Type: {attachment_type}\n"
        f"Filename: {filename}",
        ephemeral=True
    )

async def send_first_problem_to_teams(interaction: discord.Interaction, data: Dict[str, Any], flags: Dict[str, Any], order_data: Dict[str, Any]) -> int:
    """Send the first problem to all teams and return success count"""
    success_count = 0
    first_problem_name = order_data["order"][0] if order_data["order"] else None
    current_time = datetime.datetime.now().isoformat()
    
    for team_name, team_info in data["teams"].items():
        # Update all teams to start with first problem
        team_info["current_problem"] = first_problem_name
        team_info["score"] = 0
        team_info["submitted_flags"] = []
        
        # Get submission channel
        category = interaction.guild.get_channel(team_info.get("category_id"))
        if not category:
            continue
        
        submission_channel = discord.utils.get(category.channels, name="submission")
        if not submission_channel:
            continue
        
        # Send first problem
        if first_problem_name and first_problem_name in flags:
            if await send_problem(submission_channel, flags[first_problem_name], first_problem_name, team_name):
                success_count += 1
            else:
                await submission_channel.send("❌ Could not load the first problem. Contact an admin.")
    
    # Add the time to flags data
    if first_problem_name and flags[first_problem_name].get("first_access") is None:
        flags[first_problem_name]["first_access"] = current_time
        save_flags(flags)
    
    return success_count

@TREE.command(name="start_competition", description="Start the competition (admin only)")
@is_admin()
@is_admin_channel()
async def start_competition(interaction: discord.Interaction):
    """Start the competition and distribute first problems"""
    await interaction.response.defer()
    data = load_data()
    flags = load_flags()
    order_data = load_problem_order()
    
    if not flags or not order_data["order"]:
        await interaction.followup.send("❌ No problems have been added yet!", ephemeral=True)
        return

    if len(data["teams"]) == 0:
        await interaction.followup.send("❌ No teams registered yet!", ephemeral=True)
        return

    data["started"] = True
    data["paused"] = False
    save_data(data)

    success_count = await send_first_problem_to_teams(interaction, data, flags, order_data)
    
    save_data(data)
    await update_leaderboard(interaction, data)
    await interaction.followup.send(
        f"✅ Competition started! Problems sent to {success_count}/{len(data['teams'])} teams."
    )

@TREE.command(name="submit", description="Submit a flag")
async def submit(interaction: discord.Interaction, flag: str):
    """Submit a flag for the current problem"""
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    data = load_data()
    flags = load_flags()
    
    if not data.get("started", False):
        await interaction.followup.send("❌ The competition hasn't started yet!", ephemeral=True)
        return

    if data.get("paused", True):
        await interaction.followup.send("❌ The competition is paused!", ephemeral=True)
        return

    # Find user's team
    team_name = None
    for name, info in data["teams"].items():
        if user.id in info["members"]:
            team_name = name
            break

    if not team_name:
        await interaction.followup.send("❌ You're not registered in any team!", ephemeral=True)
        return

    team_info = data["teams"][team_name]
    current_problem_name = team_info["current_problem"]
    
    # Check if flag was already submitted
    if flag in team_info["submitted_flags"]:
        await interaction.followup.send("⚠️ You already submitted this flag!", ephemeral=True)
        return

    # Verify flag
    if current_problem_name not in flags:
        await interaction.followup.send("❌ No active problem found for your team!", ephemeral=True)
        return
    
    problem_data = flags[current_problem_name]
    if problem_data["flag"].lower() != flag.strip().lower():
        if not regex.match(r"dbdth\{.*\}", flag):
            await interaction.followup.send("❌ Invalid flag format! Use dbdth{...}", ephemeral=True)
            return
        # If it doesn't match, return incorrect flag message
        await interaction.followup.send("❌ Incorrect flag!", ephemeral=True)
        return

    current_time = datetime.datetime.now().isoformat()
    if problem_data.get("first_access") is None:
        problem_data["first_access"] = current_time
        save_flags(flags)

    # Update team progress
    team_info["score"] += problem_data["points"]
    team_info["submitted_flags"].append(flag)
    team_info["current_problem"] = get_next_problem_name(current_problem_name) or current_problem_name
    save_data(data)
    
    # Get submission channel
    category = interaction.guild.get_channel(team_info.get("category_id"))
    submission_channel = discord.utils.get(category.channels, name="submission") if category else None
    
    # Send success message
    embed = Embed(
        title=f"✅ Flag Accepted! {flag}",
        description=f"Your team earned {problem_data['points']} points!",
        color=discord.Color.green()
    )
    embed.add_field(
        name="New Score",
        value=f"{team_info['score']} points",
        inline=False
    )
    
    if submission_channel:
        await submission_channel.send(embed=embed)
    
    # Send next problem or completion message
    next_problem_name = team_info["current_problem"]
    if next_problem_name != current_problem_name and next_problem_name in flags:
        next_problem_data = flags[next_problem_name]
        if submission_channel:
            await send_problem(submission_channel, next_problem_data, next_problem_name, team_name)
    else:
        embed = Embed(
            title="🎉 Competition Complete!",
            description="You've solved all available problems!",
            color=discord.Color.gold()
        )
        if submission_channel:
            await submission_channel.send(embed=embed)
    
    # Update leaderboard
    await update_leaderboard(interaction, data)
    await interaction.followup.send(
        f"✅ Correct! Your team now has {team_info['score']} points.",
        ephemeral=True
    )


@TREE.command(name="register", description="Register a new team (admin only)")
@is_admin()
@is_admin_channel()
async def register(
    interaction: discord.Interaction, 
    team_name: str,
    category: Literal["fresher", "senior"],
    member1: discord.Member,
    member2: Optional[discord.Member] = None,
    member3: Optional[discord.Member] = None
):
    """Register a new team with category"""
    await interaction.response.defer()
    data = load_data()
    
    if not interaction.guild:
        await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
        return

    # Validate team name
    team_name = team_name.strip()
    if not team_name:
        await interaction.followup.send("❌ Team name cannot be empty.", ephemeral=True)
        return
    
    if len(team_name) > 32:
        await interaction.followup.send("❌ Team name must be 32 characters or less.", ephemeral=True)
        return

    # Check if team exists
    if team_name in data["teams"]:
        await interaction.followup.send("❌ Team already exists.", ephemeral=True)
        return

    # Collect non-None members
    members = [m for m in [member1, member2, member3] if m is not None]
    if not members:
        await interaction.followup.send("❌ At least one member is required.", ephemeral=True)
        return

    # Check for existing team members
    existing_members = []
    for member in members:
        if any(member.id in info["members"] for info in data["teams"].values()):
            existing_members.append(member.mention)

    if existing_members:
        await interaction.followup.send(
            f"❌ These users are already in a team: {', '.join(existing_members)}",
            ephemeral=True
        )
        return

    # Create team channels
    try:
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, manage_channels=True),
        }
        
        for member in members:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True)

        category_name = f"{team_name}"
        category_channel = await interaction.guild.create_category(category_name, overwrites=overwrites)
        await category_channel.create_text_channel("general")
        submission_channel = await category_channel.create_text_channel("submission")
        await category_channel.create_voice_channel("voice")
        hints_locked_channel = await category_channel.create_text_channel("hints")

        # Register team
        data["teams"][team_name] = {
            "members": [m.id for m in members],
            "score": 0,
            "current_problem": 1,
            "submitted_flags": [],
            "category": category,
            "category_id": category_channel.id,
            "hints_channel_id": hints_locked_channel.id,
        }
        
        save_data(data)
        
        # Send welcome message
        welcome_msg = (
            f"✅ Team '{team_name}' registered successfully as {category}!\n"
            f"**Category:** {category.capitalize()}\n"
            f"**Members:** {', '.join(m.mention for m in members)}\n"
            f"**Private channels created!**"
        )
        await submission_channel.send(welcome_msg)
        await interaction.followup.send(f"✅ Team '{team_name}' registered successfully!")

        ## if competition has started, send the first problem to this team
        if data.get("started", False):
            flags = load_flags()
            order_data = load_problem_order()
            first_problem_name = order_data["order"][0] if order_data["order"] else None
            
            if first_problem_name and first_problem_name in flags:
                data["teams"][team_name]["current_problem"] = first_problem_name
                save_data(data)
                
                if await send_problem(submission_channel, flags[first_problem_name], first_problem_name, team_name):
                    current_time = datetime.datetime.now().isoformat()
                    if flags[first_problem_name].get("first_access") is None:
                        flags[first_problem_name]["first_access"] = current_time
                        save_flags(flags)

    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ Failed to create channels: {str(e)}", ephemeral=True)
        if 'category_channel' in locals():
            await category_channel.delete()

@TREE.command(name="leaderboard", description="Show the current leaderboard")
async def show_leaderboard(interaction: discord.Interaction):
    """Display the current leaderboard with top fresher and senior teams"""
    await interaction.response.defer()
    data = load_data()

    if not data.get("teams"):
        await interaction.followup.send("No teams registered yet!")
        return

    # Separate teams by category
    fresher_teams = []
    senior_teams = []

    for team, info in data["teams"].items():
        if info.get("category") == "fresher":
            fresher_teams.append((team, info))
        else:
            senior_teams.append((team, info))

    # Sort teams by score
    fresher_teams.sort(key=lambda x: -x[1]["score"])
    senior_teams.sort(key=lambda x: -x[1]["score"])
    
    # Build leaderboard message
    leaderboard = ["🏆 **Category Winners** 🏆\n"]
    
    # Add fresher teams section
    leaderboard.append("\n**FRESHER TEAMS:**")
    if fresher_teams:
        for i, (team, info) in enumerate(fresher_teams[:5], 1):  # Top 5 fresher teams
            # members = ', '.join([f"<@{m}>" for m in info["members"]])
            leaderboard.append(
                f"{i}. **{team}** - {info['score']} points\n"
            )
    else:
        leaderboard.append("No fresher teams registered")
    
    # Add senior teams section
    leaderboard.append("\n**SENIOR TEAMS:**")
    if senior_teams:
        for i, (team, info) in enumerate(senior_teams[:5], 1):  # Top 5 senior teams
            # members = ', '.join([f"<@{m}>" for m in info["members"]])
            leaderboard.append(
                f"{i}. **{team}** - {info['score']} points\n"
            )
    else:
        leaderboard.append("No senior teams registered")
    
    # Send the leaderboard
    await interaction.followup.send('\n'.join(leaderboard))

@TREE.command(name="delete_team", description="Delete a team and its channels (admin only)")
@is_admin()
@is_admin_channel()
async def delete_team(interaction: discord.Interaction, team_name: str):
    """Delete a team and all its associated channels"""
    await interaction.response.defer()
    data = load_data()
    
    if team_name not in data["teams"]:
        await interaction.followup.send(f"❌ Team '{team_name}' not found!", ephemeral=True)

    guild = interaction.guild
    if not guild:
        await interaction.followup.send("❌ This command must be run in a server.", ephemeral=True)
        return

    team_info = data["teams"][team_name]
    
    try:
        # Delete category and all channels
        category_id = team_info.get("category_id")
        if category_id:
            category = guild.get_channel(category_id)
            if category:
                # Delete all channels in the category
                for channel in category.channels:
                    try:
                        await channel.delete()
                        print(f"Deleted channel: {channel.name}")
                    except discord.HTTPException as e:
                        print(f"Failed to delete channel {channel.name}: {str(e)}")
                
                # Delete the category itself
                try:
                    await category.delete()
                    print(f"Deleted category: {category.name}")
                except discord.HTTPException as e:
                    print(f"Failed to delete category {category.name}: {str(e)}")

        # Remove team from data
        del data["teams"][team_name]
        save_data(data)

        await interaction.followup.send(f"✅ Team '{team_name}' and all its channels have been deleted!")
        
    except Exception as e:
        error_msg = f"❌ Failed to delete team '{team_name}': {str(e)}"
        print(error_msg)
        traceback.print_exc()
        await interaction.followup.send(error_msg, ephemeral=True)

@TREE.command(name="reset_competition", description="Reset all scores and progress (admin only)")
@is_admin()
@is_admin_channel()
async def reset_competition(interaction: discord.Interaction):
    """Reset the competition"""
    await interaction.response.defer()
    data = load_data()
    flags = load_flags()
    
    for team in data["teams"].values():
        team["score"] = 0
        team["current_problem"] = 1
        team["submitted_flags"] = []
    
    for problem in flags.values():
        problem["first_access"] = None

    data["started"] = False
    save_data(data)
    
    await interaction.followup.send("✅ Competition has been reset. All scores cleared.")

@TREE.command(name="pause_competition", description="Pause the competition (admin only)")
@is_admin()
@is_admin_channel()
async def pause_competition(interaction: discord.Interaction, action: Literal["pause", "unpause"]):
    """End the competition and display final results"""
    await interaction.response.defer()
    
    data = load_data()
    try: 
        data["paused"] = True if action.lower() == "pause" else False
        save_data(data)
        await interaction.followup.send(f"✅ Competition has been {action}d successfully.")
    except Exception as e:
        await interaction.followup.send(f"❌ Competition coudn't be {action}d. Error: {e}")


@TREE.command(name="end_competition", description="End the competition and announce results (admin only)")
@is_admin()
@is_admin_channel()
async def end_competition(interaction: discord.Interaction):
    """End the competition and display final results"""
    await interaction.response.defer()
    data = load_data()
    
    if not data.get("teams"):
        await interaction.followup.send("No teams registered yet!")
        return

    data["started"] = False
    data["paused"] = True
    
    # Separate teams by category
    fresher_teams = []
    senior_teams = []
    
    for team, info in data["teams"].items():
        if info.get("category") == "fresher":
            fresher_teams.append((team, info))
        else:
            senior_teams.append((team, info))
    
    # Sort teams by score
    fresher_teams.sort(key=lambda x: -x[1]["score"])
    senior_teams.sort(key=lambda x: -x[1]["score"])
    
    # Build leaderboard message
    leaderboard = ["🏆 **Current Leaderboard** 🏆\n"]
    
    # Add fresher teams section
    leaderboard.append("\n**FRESHER TEAMS:**")
    if fresher_teams:
        for i, (team, info) in enumerate(fresher_teams[:3], 1):  # Top 3 fresher teams
            members = ', '.join([f"<@{m}>" for m in info["members"]])
            leaderboard.append(
                f"{i}. **{team}** - {info['score']} points\n"
                f"   Members: {members}"
            )
    else:
        leaderboard.append("No fresher teams registered")
    
    # Add senior teams section
    leaderboard.append("\n**SENIOR TEAMS:**")
    if senior_teams:
        for i, (team, info) in enumerate(senior_teams[:3], 1):  # Top 3 senior teams
            members = ', '.join([f"<@{m}>" for m in info["members"]])
            leaderboard.append(
                f"{i}. **{team}** - {info['score']} points\n"
                f"   Members: {members}"
            )
    else:
        leaderboard.append("No senior teams registered")

    # Send the leaderboard
    await interaction.followup.send('\n'.join(leaderboard))

@TREE.command(name="view_teams", description="View all registered teams (admin only)")
async def view_teams(interaction: discord.Interaction):
    """List all registered teams"""
    await interaction.response.defer(ephemeral=True)
    data = load_data()

    if not data["teams"]:
        await interaction.followup.send("No teams registered yet.", ephemeral=True)
        return

    embed = Embed(
        title="Registered Teams",
        color=discord.Color.blue()
    )

    for team, info in data["teams"].items():
        members = ', '.join([f"<@{m}>" for m in info["members"]])
        embed.add_field(
            name=team,
            value=f"Score: {info['score']}\nMembers: {members}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@TREE.command(name="submit_frenzy_flag", description="Submit a special 5-point flag at any time")
async def submit_frenzy_flag(interaction: discord.Interaction, flag: str):
    """Handle frenzy flag submissions"""
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    data = load_data()

    specials = data.get("special_frenzy", [])
    very_specials = data.get("very_special_frenzy", [])
    special_points = data.get("special_points", 10)
    very_special_points = data.get("very_special_points", 30)
 
    # Find user's team
    team_name = None
    team_info = None
    for name, info in data["teams"].items():
        if user.id in info["members"]:
            team_name = name
            team_info = info
            break
    
    if not team_name:
        await interaction.followup.send("❌ You're not registered in any team!", ephemeral=True)
        return
    
    # Check if flag was already submitted
    if "frenzy_flags" not in team_info:
        team_info["frenzy_flags"] = []
    
    if flag in team_info["frenzy_flags"]:
        await interaction.followup.send("⚠️ You already submitted this frenzy flag!", ephemeral=True)
        return
    
    # Verify flag
    if flag not in data.get("frenzy_flags", []):
        await interaction.followup.send("❌ Invalid frenzy flag!", ephemeral=True)
        return

    # if the competition is paused, or not started, then msg appropriate error
    if not data.get("started", False):  
        await interaction.followup.send("❌ The competition hasn't started yet!", ephemeral=True)
        return
    if data.get("paused", True):
        await interaction.followup.send("❌ The competition is paused!", ephemeral=True)
        return
    
    frenzy_points = FRENZY_POINTS
    if flag in specials:
        frenzy_points = special_points
    elif flag in very_specials:
        frenzy_points = very_special_points
    # Update team progress
    team_info["score"] += frenzy_points
    team_info["frenzy_flags"].append(flag)
    save_data(data)
  
    # Get submission channel
    category = interaction.guild.get_channel(team_info.get("category_id"))
    submission_channel = discord.utils.get(category.channels, name="submission") if category else None
    
    # Send success message
    if submission_channel:
        await submission_channel.send(
            f"🎉 **Frenzy Flag Captured!**\n"
            f"Team **{team_name}** found a special frenzy flag: {flag}!\n"
            f"+{frenzy_points} points (Total: {team_info['score']})"
        )
    await update_leaderboard(interaction, data) 
    await interaction.followup.send(
        f"✅ Correct! +{frenzy_points} points for your team! (Total: {team_info['score']})",
        ephemeral=True
    )

@TREE.command(name="add_frenzy_flag", description="Add a new frenzy flag (admin only)")
@is_admin()
@is_admin_channel()
async def add_frenzy_flag(interaction: discord.Interaction, flag: str, points: Optional[Literal[5, 10, 20]] = 5):
    """Add a new frenzy flag that can be submitted at any time"""
    await interaction.response.defer(ephemeral=True)
    data = load_data()
    
    if "frenzy_flags" not in data:
        data["frenzy_flags"] = []
    
    if flag in data["frenzy_flags"]:
        await interaction.followup.send("❌ This frenzy flag already exists!", ephemeral=True)
        return

    if regex.match(r"dbdth\{.*\}", flag) is None:
        await interaction.followup.send("❌ Invalid frenzy flag format! Use dbdth{...}", ephemeral=True)
        return

    # Add the new frenzy flag
    if points == 20:
        data["very_special_frenzy"].append(flag)
    elif points == 10:
        data["special_frenzy"].append(flag)
    data["frenzy_flags"].append(flag)
    save_data(data)
    
    await interaction.followup.send(f"✅ Frenzy flag '{flag}' added successfully!", ephemeral=True)

@TREE.command(name="hint", description="Post a text hint to all teams (admin only)")
@is_admin()
@is_admin_channel()
async def post_hint(
    interaction: discord.Interaction,
    hint_text: str,
    problem_name: str,
    updated_points: Optional[int] = PROBLEM_POINTS
):
    """Post a text hint to all teams' hint channels"""
    await interaction.response.defer()
    data = load_data()
    flag_data = load_flags()
    
    if not interaction.guild:
        await interaction.followup.send("❌ This command must be used in a server.", ephemeral=True)
        return

    # Format the hint message
    hint_message = (
        f"💡 **OFFICIAL HINT FOR {problem_name.upper()}** 💡\n"
        f"{hint_text}\n\n"
        f"⚠️ **New problem value:** {updated_points} points\n"
    )

    flag_data[problem_name]["points"] = updated_points
    save_flags(flag_data)

    try:
        # Post in the channel where command was run
        await interaction.followup.send(hint_message)
        
        # Post in each team's hints channel
        for team_name, team_info in data["teams"].items():
            category = interaction.guild.get_channel(team_info.get("category_id"))
            if not category:
                continue
                
            # Find or create hints channel
            hints_channel = discord.utils.get(category.channels, name="hints")
            if not hints_channel:
                # Create locked hints channel if it doesn't exist
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=False
                    ),
                    interaction.guild.me: discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=True
                    )
                }
                hints_channel = await category.create_text_channel(
                    "hints",
                    overwrites=overwrites,
                    reason="Auto-created hints channel"
                )
                # Add channel to team info
                team_info["hints_channel_id"] = hints_channel.id
                save_data(data)
            
            # Send the hint with team-specific header
            team_hint = (
                f"📌 **For Team {team_name}:**\n"
                f"{hint_message}"
            )
            await hints_channel.send(team_hint)
            
        await interaction.followup.send("✅ Hint posted to all teams!", ephemeral=True)
        
    except Exception as e:
        error_msg = f"❌ Failed to post hints: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        await interaction.followup.send(error_msg, ephemeral=True)

@TREE.command(name="problem_stats", description="Show problem-solving statistics (admin only)")
@is_admin()
@is_admin_channel()
async def problem_stats(interaction: discord.Interaction):
    """Display problem solve rates and time since release with proper chunking"""
    try:
        # Initial deferral
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        flags = load_flags()
        order_data = load_problem_order()

        if not data.get("started", False):
            await interaction.followup.send("❌ Competition hasn't started yet!", ephemeral=True)
            return

        # Prepare statistics data
        headers = ["Problem", "Solved", "Solve %", "Teams", "Time Since Release"]
        max_name_length = 15  # Maximum characters for problem names
        rows = []
        
        for problem_name in order_data["order"]:
            if problem_name not in flags:
                continue
                
            # Count teams that have solved this problem (progressed past it or solved it specifically)
            solved_by = 0
            for team in data["teams"].values():
                # Check if team has problem-specific solve time recorded
                if problem_name in team and "solve_time" in team[problem_name]:
                    solved_by += 1
                # Alternative: check if current problem is past this one
                elif team.get("current_problem"):
                    try:
                        current_idx = order_data["order"].index(team["current_problem"])
                        problem_idx = order_data["order"].index(problem_name)
                        if current_idx > problem_idx:
                            solved_by += 1
                    except ValueError:
                        pass
            total_teams = len(data["teams"])
            
            # Calculate time since release
            time_elapsed = "N/A"
            if flags[problem_name].get("first_access"):
                first_access_time = datetime.datetime.fromisoformat(flags[problem_name]["first_access"])
                time_elapsed = str(datetime.datetime.now() - first_access_time).split('.')[0]

            rows.append([
                problem_name[:max_name_length],
                str(solved_by),
                f"{solved_by/total_teams*100:.1f}%" if total_teams else "0%",
                f"{solved_by}/{total_teams}",
                time_elapsed
            ])

        # Calculate max column widths
        col_widths = [len(str(x)) for x in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Format as aligned text table with limited width
        def create_table_section(rows_chunk, include_headers=True):
            """Create a formatted table section"""
            # Header line
            if include_headers:
                header_line = "| " + " | ".join(
                    h.center(col_widths[i]) for i, h in enumerate(headers)
                ) + " |"
                separator_line = "+-" + "-+-".join(
                    "-"*w for w in col_widths
                ) + "-+"
                table = [header_line, separator_line]
            else:
                table = []
            
            # Add rows
            for row in rows_chunk:
                table.append("| " + " | ".join(
                    str(cell).center(col_widths[i]) for i, cell in enumerate(row)
                ) + " |")
            return "\n".join(table)

        # Split rows into chunks that fit Discord's limits
        chunk_size = 15  # Conservative row count per message
        total_chunks = (len(rows) + chunk_size - 1) // chunk_size
        
        # Send initial header
        await interaction.followup.send(
            f"**📊 Problem Statistics** ({len(rows)} problems)",
            ephemeral=True
        )

        # Send table chunks
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            chunk = rows[start_idx:end_idx]
            
            table_chunk = create_table_section(
                chunk,
                include_headers=(i == 0)  # Only show headers first time
            )
            
            message = f"```\n{table_chunk}\n```"
            if len(message) > 2000:
                # Fallback if our calculation was off
                message = message[:1990] + "\n```"  # Truncate safely
            
            await interaction.followup.send(message, ephemeral=True)
            
            # Small delay between messages to avoid rate limiting
            if i < total_chunks - 1:
                await asyncio.sleep(1)

    except Exception as e:
        error_msg = f"❌ Error generating stats: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)

@TREE.command(name="view_all_problems", description="View all problems (admin only)")
@is_admin()
@is_admin_channel()
async def view_all_problems(interaction: discord.Interaction):
    """Send all problems to the admin"""
    try:
        await interaction.response.defer(ephemeral=True)
        flags = load_flags()
        order_data = load_problem_order()
        
        if not flags:
            await interaction.followup.send("❌ No problems have been added yet!", ephemeral=True)
            return

        # Create temporary channel for admin
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
        
        temp_category = await interaction.guild.create_category(
            name=f"temp-problems-{interaction.user.name}",
            overwrites=overwrites
        )
        temp_channel = await temp_category.create_text_channel("all-problems")
        
        await interaction.followup.send(
            f"📚 All problems will be shown in {temp_channel.mention}",
            ephemeral=True
        )
        
        # Send each problem
        for problem_name in order_data["order"]:
            if problem_name in flags:
                problem_data = flags[problem_name]
                success = await send_problem(
                    channel=temp_channel,
                    problem_data=problem_data,
                    problem_name=problem_name,
                    team_name="ADMIN"
                )
                if not success:
                    await temp_channel.send(f"❌ Failed to load problem: {problem_name}")
                await asyncio.sleep(1)  # Rate limiting
        
        # Add auto-deletion note
        await temp_channel.send(
            "\n⚠️ This temporary channel will be deleted in 10 minutes. "
            "Use `/save_problems` to export all problems to files."
        )
        

    except Exception as e:
        error_msg = f"❌ Failed to show problems: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)


if __name__ == "__main__":
    if not os.path.exists(PROBLEMS_FOLDER):
        os.makedirs(PROBLEMS_FOLDER)
    
    # Load initial data
    load_data()
    load_flags()
    
    # Start the bot
    bot.run(TOKEN)
