#include <Keypad.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <LiquidCrystal_I2C.h>

// Set these to your desired credentials.
const char *ssid = "Silas";
const char *password = "whatever!"; // Replace with your actual Wi-Fi password

// Define keypad configuration
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  { '1', '2', '3', 'A' },
  { '4', '5', '6', 'B' },
  { '7', '8', '9', 'C' },
  { '*', '0', '#', 'D' }
};
byte rowPins[ROWS] = { 33, 25, 26, 14 };
byte colPins[COLS] = { 27, 13, 16, 4 };

// Initialize keypad object
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Initialize WiFi client and receiver details
WiFiClient client;
const char *receiverIP = "172.20.10.6";  // Replace with actual IP
const int receiverPort = 33455;

// Define variables for current state of the system
String inputToken = "";  // Buffer for user input token
int currentToken = 0;    // Current token being served
int counterID = 1;

// Initialize LCD object
LiquidCrystal_I2C lcd(0x27, 16, 2); // Address 0x27, 16 columns, 2 rows

void transmitData(int token, int counter);
void printMessage(const char* message);
void scrollMessage(const char* message, int row);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  // Connect to WiFi network
  connectToWiFi();

  // Initialize LCD
  lcd.init();
  lcd.backlight(); // Turn on 
  lcd.clear(); // Clear display
}

void loop() {
  // Get key pressed from keypad
  char key = keypad.getKey();

  // Check if a key is pressed
  if (key) {
    // Check if the pressed key is 'A' for manual token entry
    if (key == 'A') {
      // Convert input to integer
      int enteredToken = inputToken.toInt();
      // Check if entered token is greater than 100
      if (enteredToken < 100) {
        // Transmit manually entered token and counter
        transmitData(enteredToken, counterID);
        inputToken = ""; // Clear input token buffer
      } else {
        printMessage("Please enter a number less than 100");
        inputToken = ""; // Clear input token buffer
      }
    } else if (key == 'B') { // Check if the pressed key is 'B' for token increment
      // Increment token and reset to 1 if it reaches 100
      currentToken = (currentToken % 100) + 1;
      // Transmit incremented token along with random counter number
      transmitData(currentToken, counterID);  // Random counter number between 1 and 4
    } else if (isdigit(key) || key == '*') { // Check if the pressed key is a digit or '*'
      // Append numeric key press to input token buffer
      inputToken += key;
      // Print current input token for feedback
      Serial.println("Current input token: " + inputToken);
    } else { // Handle invalid key press
      Serial.println("Invalid key press!");
    }
  }
}

// Function to connect to WiFi network
void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 5) {
    delay(1000 * (attempts + 1)); // Exponential backoff
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect to WiFi.");
  } else {
    Serial.println("Connected to WiFi");
  }
}

// Function to transmit data to receiver
void transmitData(int token, int counter) {
  // Check if client is connected to WiFi
  if (!client.connected()) {
    // Attempt to reconnect if not connected
    if (!client.connect(receiverIP, receiverPort)) {
      printMessage("Failed to connect to receiver.");
      return;
    }
  }
  // Send data to receiver
  String mess = String(counter) + "," + String(token);
  Serial.println(mess);
  client.println(mess);

  // Print transmitted data on LCD
  lcd.clear();
  lcd.setCursor(0, 0); // Set cursor to first column-row
  lcd.print("Token: ");
  lcd.print(token);
}

// Function to print message on LCD
void printMessage(const char* message) {
  lcd.clear();
  scrollMessage(message, 0);
}

// Function to scroll message on LCD
void scrollMessage(const char* message, int row) {
  int len = strlen(message);
  if (len <= 16) {
    lcd.setCursor(0, row);
    lcd.print(message);
    return;
  }
  
  for (int i = 0; i < len - 16 + 1; i++) {
    lcd.setCursor(0, row);
    lcd.print(message + i);
    delay(300);
  }

  delay(1000);
  
  for (int i = 0; i < 16; i++) {
    lcd.scrollDisplayLeft();
    delay(300);
  }

  lcd.clear();
}

