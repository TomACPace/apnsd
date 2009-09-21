//
//  APNSTestAppDelegate.m
//  APNSTest
//
//  Created by Sri Panyam on 6/09/09.
//  Copyright __MyCompanyName__ 2009. All rights reserved.
//

#import "APNSTestAppDelegate.h"

@implementation APNSTestAppDelegate

@synthesize window, theTextView, baseUrlTextView;
@synthesize toggleNotificationSwitch;

- (void)applicationDidFinishLaunching:(UIApplication *)application 
{
	[ toggleNotificationSwitch setOn:NO ];
    // Override point for customization after application launch
	// [self loadView];
	self->deviceTokenString = [[NSMutableString alloc] initWithString:@""];
	[theTextView setScrollEnabled:YES];
	[theTextView setEditable:NO];
	
    [window makeKeyAndVisible];
}

- (IBAction)togglePushNotification:(id)sender
{
	UIApplication *sharedApplication = [UIApplication sharedApplication];
	UISwitch *theSwitch = (UISwitch *)sender;
	UIAlertView *alertView;
	BOOL on = theSwitch.isOn;
	if (on)
	{
		alertView = [[UIAlertView alloc] initWithTitle:@"Registering APNS" message:@"Oh boy you will just love APNS!!!" delegate:nil cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[sharedApplication registerForRemoteNotificationTypes:(UIRemoteNotificationTypeAlert |
															   UIRemoteNotificationTypeBadge |
															   UIRemoteNotificationTypeSound)];
	}
	else
	{
		alertView = [[UIAlertView alloc] initWithTitle:@"UnRegistering APNS" message:@"Thanks for using Push Notification" delegate:nil cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[sharedApplication unregisterForRemoteNotifications];
		if ([deviceTokenString length] > 0)
		{
			NSString *url = [NSString stringWithFormat:@"http://%@/devices/unregister/%@/", baseUrlTextView.text, deviceTokenString, nil];
			NSURLRequest *request = [[NSURLRequest alloc] initWithURL:
									 [[NSURL alloc] initWithString:url]];
			NSURLConnection *connection = [[NSURLConnection alloc] initWithRequest:request delegate:nil];
			[self appendTextView:@"\nNoooooooo dont leave me.....   Il do anyting you say!!!"];
			[connection release];
			[request release];
			[deviceTokenString setString:@""];
			[self appendTextView:@"\n--------------"];
		}
	}
	// [alertView show];
	[alertView release];
}

- (void)dealloc {
    [window release];
    [super dealloc];
}

- (void)appendTextView:(NSString *)withString
{
	NSMutableString *oldText = [[NSMutableString alloc] initWithString:theTextView.text];
	[oldText appendString:withString];
	theTextView.text = oldText;
}

- (void)setDeviceTokenString:(NSData *)deviceToken
{
	char *hexChars = "0123456789ABCDEF";
	[deviceTokenString setString:@""];
	for (int i = 0;i < deviceToken.length;i++)
	{
		unsigned currChar = ((unsigned char *)deviceToken.bytes)[i];
		[deviceTokenString appendFormat:@"%c%c", hexChars[currChar / 16], hexChars[currChar % 16]];
	}
}

- (void)application:(UIApplication *)application didRegisterForRemoteNotificationsWithDeviceToken:(NSData *)deviceToken 
{
	self.deviceTokenString = deviceToken;
	NSString *url = [NSString stringWithFormat:@"http://%@/devices/register/%@/", baseUrlTextView.text, deviceTokenString, nil];
	NSURLRequest *request = [[NSURLRequest alloc] initWithURL:
								[[NSURL alloc] initWithString:url]];
	NSURLConnection *connection = [[NSURLConnection alloc] initWithRequest:request delegate:nil];
	[self appendTextView:@"\nBoy oh Boy.  You are so gonna love push notifications!!!"];
	[self appendTextView:@"\nDevice Token: "];
	[self appendTextView:deviceTokenString];
	[self appendTextView:@"\n--------------"];
	[connection release];
	[request release];
}

- (void)application:(UIApplication *)application didFailToRegisterForRemoteNotificationsWithError:(NSError *)error 
{
	UIAlertView *alertView = [[UIAlertView alloc] initWithTitle:@"Registration Failed" message:@"Error in registering for Push Notification" delegate:nil cancelButtonTitle:@"OK" otherButtonTitles:nil];
	NSString *localizedDescription = [error localizedDescription];
	NSString *localizedFailureReason = [error localizedFailureReason];
	NSString *localizedRecoverySuggestion = [error localizedRecoverySuggestion];
	NSLog(@"Description -------------------------------------");
	NSLog(localizedDescription);
	NSLog(@"Failure Reason -------------------------------------");
	NSLog(localizedFailureReason);
	NSLog(@"Recovery Suggestion -------------------------------------");
	NSLog(localizedRecoverySuggestion);
	NSLog(@"-------------------------------------");
	// [alertView setMessage:[error localizedDescription]];
	// [alertView show];
	// [alertView setMessage:[error localizedFailureReason]];
	// [alertView show];
	[alertView setMessage:[error localizedRecoverySuggestion]];
	[alertView show];
	[alertView release];
}

- (void)application:(UIApplication *)application didReceiveRemoteNotification:(NSDictionary *)userInfo 
{
	
	[ self appendTextView:@"\nYep you got notificationafied!!!  Do something pretty with the payload." ];
	[self appendTextView:@"\n--------------"];
}

@end
