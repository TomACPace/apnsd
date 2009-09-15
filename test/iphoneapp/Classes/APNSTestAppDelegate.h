//
//  APNSTestAppDelegate.h
//  APNSTest
//
//  Created by Sri Panyam on 6/09/09.
//  Copyright __MyCompanyName__ 2009. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface APNSTestAppDelegate : NSObject <UIApplicationDelegate> {
    UIWindow *window;
	UITextView *theTextView;
	UISwitch *toggleNotificationSwitch;
	NSMutableString *deviceTokenString;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet UITextView *theTextView;
@property (nonatomic, retain) IBOutlet UISwitch *toggleNotificationSwitch;

-(IBAction)togglePushNotification:(id)sender;
- (void)appendTextView:(NSString *)withString;

@end

