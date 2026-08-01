#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "bad_apple_rle.h" 

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET    -1 
#define OLED_ADDR     0x3C

// ESP32 I2C Pins
#define I2C_SDA 21
#define I2C_SCL 22

// Only define 'display' once!
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void drawRLEFrame(int frameNumber) {
    uint32_t offset = pgm_read_dword(&(frame_offsets[frameNumber]));
    uint32_t nextOffset = pgm_read_dword(&(frame_offsets[frameNumber + 1]));
    uint32_t frameSize = nextOffset - offset;

    int pixelIndex = 0;
    
    for (uint32_t i = 0; i < frameSize; i++) {
        uint8_t packet = pgm_read_byte(&(bad_apple_rle[offset + i]));
        
        uint8_t color = (packet & 0x80) ? SSD1306_WHITE : SSD1306_BLACK;
        uint8_t count = (packet & 0x7F);

        for (uint8_t j = 0; j < count; j++) {
            if (pixelIndex < (SCREEN_WIDTH * SCREEN_HEIGHT)) {
                int x = pixelIndex % 128;
                int y = pixelIndex / 128;
                display.drawPixel(x, y, color);
                pixelIndex++;
            }
        }
    }
}

void setup() {
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000); 

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    for (;;); 
  }

  display.clearDisplay();
  display.display();
}

void loop() {
    for (int i = 0; i < 6527; i++) {
        display.clearDisplay(); 
        drawRLEFrame(i);
        display.display(); 
        //delay(5);
    }
}