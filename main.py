import os
import asyncio
import discord
from datetime import datetime, time, timedelta
from discord.ext import commands, tasks

from user_manager import UserManager
from user import User
from pod import Pod
from utils import ExtendPodSelectView, StopPodSelectView
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


BOT_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Set up the bot
bot = commands.Bot(command_prefix='/', intents=intents)
# Init users
users = UserManager()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    # Start the pod expiration checker task
    if not pod_checker.is_running():
        pod_checker.start()
    if not daily_running_pod_notifier.is_running():
        daily_running_pod_notifier.start()


# Create /start command to start a pod
@bot.tree.command(name="start", description="Start a pod")
@discord.app_commands.describe(
    name="The name of the pod",
    cloud="The cloud provider",
    gpu="The GPU type",
    number_of_gpu="The number of GPUs",
    time_hours="The duration in hours"
)
async def start(
    interaction: discord.Interaction,
    name: str,
    cloud: str,
    gpu: str,
    number_of_gpu: int,
    time_hours: float
):
    
    # Add user to users
    if not users.check_user_exist(interaction.user.id):
        users.add_user(User(interaction.user.id))

    # Add pod to user
    user = users.get_user(interaction.user.id)
    pod = Pod(interaction.user.id, name, number_of_gpu, cloud, gpu, time_hours)
    user.add_pod(pod)
    
    user_mention = interaction.user.mention
    message = (
        f"{user_mention} starting a pod: \n"
        f"{pod.get_detail_info()}"
    )
    await interaction.response.send_message(message)
    

# Add autocomplete for cloud providers
@start.autocomplete("cloud")
async def cloud_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[discord.app_commands.Choice[str]]:
    clouds = ["Runpod", "TensorDock","AWS", "Azure", "GCP"]
    return [
        discord.app_commands.Choice(name=cloud, value=cloud)
        for cloud in clouds
        if current.lower() in cloud.lower()
    ]


# Add autocomplete for GPU types
@start.autocomplete("gpu")
async def gpu_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[discord.app_commands.Choice[str]]:
    gpus = [
        "A100 PCIe",
        "A100 SXM",
        "H100 PCIe",
        "H100 SXM",
        "L40",
        "L40S",
        "MI300X",
        "RTX 2000 Ada",
        "RTX 3090",
        "RTX 4090",
        "RTX 6000 Ada",
        "RTX A6000",
        "CPU"
    ]
    return [
        discord.app_commands.Choice(name=gpu, value=gpu)
        for gpu in gpus
        if current.lower() in gpu.lower()
    ]
    

# Create /extend command to extend a pod's duration
@bot.tree.command(name="extend", description="Extend the duration of a pod")
async def extend(interaction: discord.Interaction):
    user_mention = interaction.user.mention
    user = users.get_user(interaction.user.id)

    if not user or not user.pods:
        await interaction.response.send_message(f"{user_mention}, you have no active pods to extend.")
        return

    # Send the dropdown menu to the user
    await interaction.response.send_message(
        f"{user_mention}, please select a pod to extend:",
        view=ExtendPodSelectView(user)
    )


# Create /stop command to stop a pod
@bot.tree.command(name="stop", description="Stop a pod")
async def stop(interaction: discord.Interaction):
    user_mention = interaction.user.mention
    user = users.get_user(interaction.user.id)

    if not user or not user.pods:
        await interaction.response.send_message(f"{user_mention}, you have no active pods to stop.")
        return

    # Send the dropdown menu to the user
    await interaction.response.send_message(
        f"{user_mention}, please select a pod to stop:",
        view=StopPodSelectView(user),
    )
    
    
# Background task to check for expired pods
@tasks.loop(minutes=1)
async def pod_checker():
    print("Running pod expiration checker...")
    channel_id = CHANNEL_ID
    channel = bot.get_channel(channel_id)

    if not channel:
        print(f"Channel with ID {channel_id} not found.")
        return

    for user in users.users.values():
        expired_pods = [pod for pod in user.pods if pod.is_over_stop_time()]
        if expired_pods:
            expired_pod_names = "\n".join([f"{pod.get_id()}" for pod in expired_pods])
            await channel.send(
                f"{bot.get_user(user.id).mention}, your pod(s): \n`{expired_pod_names}`\nhave expired. Please stop them.",
                delete_after=60.0
            )
            
            
# Daily notification of users with active pods at 7 PM
@tasks.loop(minutes=1)
async def daily_running_pod_notifier():
    now = datetime.now()
    target_time = time(19, 0)  # 7:00 PM
    # Check if the current time is 7 PM ± 1 minute
    if now.time() >= target_time and now.time() <= (datetime.combine(datetime.today(), target_time) + timedelta(minutes=1)).time():
        print("Running daily running pod notifier...")
        channel_id = CHANNEL_ID
        channel = bot.get_channel(channel_id)

        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            return

        active_users = []
        for user in users.users.values():
            if user.pods:
                active_pod_names = "\n".join([f"{pod.get_short_info()}" for pod in user.pods])
                active_users.append(f"{bot.get_user(user.id).mention}: {active_pod_names}")

        if active_users:
            message = "📢 **Daily Running Pods Notification** 📢\n" + "\n".join(active_users)
        else:
            message = "📢 **Daily Running Pods Notification** 📢\nNo active pods found."

        await channel.send(message)


bot.run(BOT_TOKEN)
