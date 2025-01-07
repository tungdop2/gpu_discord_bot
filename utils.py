import discord


# Create a dropdown menu to extend pod duration
class ExtendPodSelectView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.pods = user.pods

        options = [
            discord.SelectOption(label=pod.name, description=f"{pod.get_short_info()}", value=str(index))
            for index, pod in enumerate(self.pods)
        ]
        
        self.add_item(ExtendPodSelectDropdown(options, self.user))
            
class ExtendPodSelectDropdown(discord.ui.Select):
    def __init__(self, options, user):
        super().__init__(placeholder="Select a pod to extend", options=options)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        pod = self.user.pods[selected_index]

        # Open a modal to input the extension time
        await interaction.response.send_modal(ExtendPodModal(pod))
        
        await interaction.message.delete()
        
class ExtendPodModal(discord.ui.Modal, title="Extend Pod Duration"):
    def __init__(self, pod):
        super().__init__()
        self.pod = pod

        # Add an input field for hours
        self.extend_time_input = discord.ui.TextInput(
            label="Additional Hours",
            placeholder="Enter the number of hours to extend",
            required=True
        )
        self.add_item(self.extend_time_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            additional_hours = float(self.extend_time_input.value)

            # Extend the pod's duration
            self.pod.extend_time(additional_hours)

            await interaction.response.send_message(
                f"Pod `{self.pod.get_id()}` has been extended by `{additional_hours}` hours. "
                f"New stop time: `{self.pod.get_should_stopped_at().strftime('%Y-%m-%d %H:%M:%S')}`."
            )
        except ValueError:
            await interaction.response.send_message(
                f"Invalid input. Please provide a valid number of hours.",
                ephemeral=True
            )
            
# Create a dropdown menu to stop a pod
class StopPodSelectView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.pods = user.pods

        options = [
            discord.SelectOption(label=pod.name, description=f"{pod.get_short_info()}", value=str(index))
            for index, pod in enumerate(self.pods)
        ]
        self.add_item(StopPodSelectDropdown(options, self.user))

class StopPodSelectDropdown(discord.ui.Select):
    def __init__(self, options, user):
        super().__init__(placeholder="Select a pod to stop", options=options)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        pod = self.user.pods[selected_index]

        # Remove the pod from the user's list
        self.user.remove_pod(pod)
        await interaction.response.send_message(
            f"Pod `{pod.get_id()}` has been stopped."
        )
        
        await interaction.message.delete()
