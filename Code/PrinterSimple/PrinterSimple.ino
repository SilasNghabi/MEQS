
#include "Adafruit_Thermal.h"
#include "SoftwareSerial.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Define the RX and TX pins for software serial communication
#define TX_PIN 6  // Connect to printer RX
#define RX_PIN 13  // Not used in this example

// Define the push button pin
#define BUTTON_PIN 2

// Create a SoftwareSerial object
SoftwareSerial mySerial(RX_PIN, TX_PIN);

// Create an Adafruit_Thermal object
Adafruit_Thermal printer(&mySerial);

// Create an LCD object
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16 chars and 2 line display

int tokenNumber = 1;

void setup() {
  // Start the software serial communication
  mySerial.begin(9600);  // Default baudrate for the printer

  // Initialize the printer
  printer.begin();
  
  // Initialize the LCD
  lcd.init();
  lcd.backlight();

  // Display the welcome messages on the LCD
  showWelcomeMessages();

  // Set the button pin as input with internal pull-up resistor
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  // Check if the button is pressed (LOW state)
  if (digitalRead(BUTTON_PIN) == LOW) {
    // Debounce the button
    delay(50);
    if (digitalRead(BUTTON_PIN) == LOW) {
      printToken();
      tokenNumber++; // Increment the token number
      if (tokenNumber > 100) {
        tokenNumber = 1; // Restart the token number after 100
      }
      // Wait for the button to be released
      while (digitalRead(BUTTON_PIN) == LOW);
      delay(50); // Debounce the release
    }
  }
}

void printToken() {
  // Create a char array to hold the formatted token number
  char tokenString[4];  // 3 digits + null terminator
  sprintf(tokenString, "%03d", tokenNumber);  // Format the number with leading zeros
  printer.justify('C');  // Center align text
  printer.println("UDSM QUEUING SYSTEM");
  printer.println("Date: " __DATE__ " Time: " __TIME__);
  printer.println("**********************************");
  printer.justify('C');  // Center align text
  printer.println("TICKET NO: ");
  printer.setSize('L');  // Set text size to large
  printer.justify('C');  // Center align text
  // Print the token number with larger font size
  printer.println(tokenString);
  printer.setSize('S');  // Set text size to small
  printer.println("**********************************");
  printer.justify('C');  // Center align text
  printer.println("KARIBU|WELCOME");
  printer.println();
  printer.feed(2); // Feed a few lines to provide spacing
}

// Function to scroll a message on a specific row of the LCD
void scrollMessage(const char* message, int row, int delayTime = 300) {
  int len = strlen(message);
  if (len <= 16) {
    lcd.setCursor(0, row);
    lcd.print(message);
    delay(delayTime);
    return;
  }
  
  for (int i = 0; i < len - 16 + 1; i++) {
    lcd.setCursor(0, row);
    for (int j = 0; j < 16; j++) {
      if (i + j < len) {
        lcd.print(message[i + j]);
      } else {
        lcd.print(" ");
      }
    }
    delay(delayTime);
  }

  delay(1000);
  
  lcd.clear();
}

// Function to show the welcome messages
void showWelcomeMessages() {
  lcd.clear();
  scrollMessage("KARIBU!", 0, 1000);
  lcd.clear();
  scrollMessage("Bonyeza kitufe kuchukua tiketi", 0);
  lcd.clear();
  scrollMessage("WELCOME!", 0, 1000);
  lcd.clear();
  scrollMessage("Press button to collect ticket", 0);
}
