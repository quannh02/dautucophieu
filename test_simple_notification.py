#!/usr/bin/env python3
"""
Simple Notification Test - No heavy dependencies
"""

import subprocess
import platform
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_macos_notification():
    """Test macOS notification directly"""
    print("🧪 Testing macOS Notification...")
    
    try:
        if platform.system() == "Darwin":  # macOS
            title = "🚨 Crypto Alert Test"
            message = "Desktop notification error has been fixed!"
            
            # Escape quotes in the message
            title_escaped = title.replace('"', '\\"')
            message_escaped = message.replace('"', '\\"')
            
            script = f'''
            display notification "{message_escaped}" with title "{title_escaped}" sound name "default"
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                         capture_output=True, 
                         timeout=5,
                         text=True)
            
            if result.returncode == 0:
                print("✅ macOS notification sent successfully!")
                print("🔔 You should see a notification in the top-right corner")
                return True
            else:
                print(f"❌ Error: {result.stderr}")
                return False
        else:
            print("❌ Not running on macOS")
            return False
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def test_plyer_notification():
    """Test plyer notification"""
    print("\n🧪 Testing Plyer Notification...")
    
    try:
        from plyer import notification
        
        notification.notify(
            title="🚨 Crypto Alert Test",
            message="Testing plyer notification system",
            timeout=10,
            app_name="Crypto Trading Alert"
        )
        print("✅ Plyer notification sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Plyer notification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Notification Test")
    print("=" * 40)
    
    # Test macOS notification
    macos_success = test_macos_notification()
    
    # Test plyer notification
    plyer_success = test_plyer_notification()
    
    print("\n📊 Results:")
    print(f"macOS notification: {'✅ Working' if macos_success else '❌ Failed'}")
    print(f"Plyer notification: {'✅ Working' if plyer_success else '❌ Failed'}")
    
    if macos_success or plyer_success:
        print("\n🎉 At least one notification method is working!")
        print("The desktop notification error has been resolved.")
    else:
        print("\n⚠️  No notification methods are working.")
        print("You can disable desktop notifications in config.py:")
        print("ENABLE_DESKTOP_NOTIFICATIONS = False") 