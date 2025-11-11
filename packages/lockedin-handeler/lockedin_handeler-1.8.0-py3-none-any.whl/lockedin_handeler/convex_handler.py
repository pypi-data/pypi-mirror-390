"""
Convex Space Manager - Core functionality for managing space availability in Convex.
"""

import json
from convex import ConvexClient


class ConvexSpaceManager:
    """
    A simple class to manage space availability in Convex.
    """
    
    def __init__(self, deployment_url: str):
        self.client = ConvexClient(deployment_url)
    
    def update_space(self, space_name: str, is_full: bool):
        try:
            self.client.mutation("spaces:update_fullness", {
                "spaceName": space_name,
                "isFull": is_full
            })
            print(f"[SUCCESS] Updated {space_name}: {'Full' if is_full else 'Available'}")
        except Exception as e:
            print(f"[ERROR] Error updating {space_name}: {e}")
    
    def update_multiple_spaces(self, space_names: list[str], availability_flags: list[bool]):
       
        if len(space_names) != len(availability_flags):
            raise ValueError("Number of space names must match number of availability flags")
        
        print(f"Updating {len(space_names)} spaces...")
        for i, (name, is_full) in enumerate(zip(space_names, availability_flags)):
            self.update_space(name, is_full)
        print("All spaces updated!")
    def add_lp(self, lp_num: str):
        try:
            self.client.mutation("")

def convex_sync(flags: list[bool], names: list[str], deployment_url: str = None):
    if deployment_url is None:
        raise ValueError("You must provide your Convex deployment URL! Replace 'https://your-deployment.convex.cloud' with your actual URL.")
    
    manager = ConvexSpaceManager(deployment_url)
    manager.update_multiple_spaces(names, flags)
