#include <Servo.h>
#include <string.h>
#include <stdlib.h>


// ============================================================
// SERVO PINS
// ============================================================

#define X_SERVO_PIN 5
#define Y_SERVO_PIN 6


// ============================================================
// RGB LED PINS
// ============================================================

#define RED_PIN 9
#define GREEN_PIN 11
#define BLUE_PIN 10


// ============================================================
// SERVO OBJECTS
// ============================================================

Servo servoX;
Servo servoY;


// ============================================================
// SERVO LIMITS
// ============================================================

const float X_MIN = 30;
const float X_MAX = 150;

const float Y_MIN = 0;
const float Y_MAX = 70;


// ============================================================
// STARTING POSITION
// ============================================================

float servoXPos = 90;
float servoYPos = 35;


// ============================================================
// PID GAINS
// ============================================================

float Kp_X = 0.030;
float Kd_X = 0.005;

float Kp_Y = 0.010;
float Kd_Y = 0.005;


// Integral disabled

float Ki_X = 0.0;
float Ki_Y = 0.0;


// ============================================================
// MAXIMUM SERVO MOVEMENT
// ============================================================

const float MAX_STEP_X = 1.2;
const float MAX_STEP_Y = 2.0;


// ============================================================
// DEAD ZONE
// ============================================================

const float DEAD_ZONE_X = 30;
const float DEAD_ZONE_Y = 30;


// ============================================================
// PID VARIABLES
// ============================================================

float errorX = 0;
float errorY = 0;

float previousErrorX = 0;
float previousErrorY = 0;

float integralX = 0;
float integralY = 0;


// ============================================================
// DERIVATIVE FILTER
// ============================================================

float filteredDerivativeX = 0;
float filteredDerivativeY = 0;

const float DERIVATIVE_FILTER = 0.25;


// ============================================================
// TIMING
// ============================================================

unsigned long lastPIDTime = 0;

const unsigned long PID_INTERVAL = 20;


// ============================================================
// SERIAL BUFFER
// ============================================================

char serialBuffer[40];

byte bufferIndex = 0;


// ============================================================
// LED STATE
// ============================================================

String currentLED = "";


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);


    // --------------------------------------------------------
    // SERVOS
    // --------------------------------------------------------

    servoX.attach(X_SERVO_PIN);
    servoY.attach(Y_SERVO_PIN);


    servoX.write(
        (int)servoXPos
    );

    servoY.write(
        (int)servoYPos
    );


    // --------------------------------------------------------
    // RGB LED
    // --------------------------------------------------------

    pinMode(
        RED_PIN,
        OUTPUT
    );

    pinMode(
        GREEN_PIN,
        OUTPUT
    );

    pinMode(
        BLUE_PIN,
        OUTPUT
    );


    // Start with BLUE

    setLED("BLUE");


    lastPIDTime = millis();


    Serial.println(
        "FACE ROBOT READY"
    );
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop()
{
    // --------------------------------------------------------
    // READ SERIAL
    // --------------------------------------------------------

    readSerial();


    // --------------------------------------------------------
    // PID UPDATE
    // --------------------------------------------------------

    unsigned long now = millis();


    if (
        now - lastPIDTime
        >= PID_INTERVAL
    )
    {
        float dt =
            (now - lastPIDTime)
            / 1000.0;


        lastPIDTime = now;


        updatePID(dt);
    }
}


// ============================================================
// SERIAL READER
// ============================================================

void readSerial()
{
    while (
        Serial.available() > 0
    )
    {
        char c = Serial.read();


        // ----------------------------------------------------
        // END OF COMMAND
        // ----------------------------------------------------

        if (c == '\n')
        {
            serialBuffer[bufferIndex] = '\0';


            // Check whether this is
            // an LED command

            if (
                strncmp(
                    serialBuffer,
                    "LED:",
                    4
                ) == 0
            )
            {
                processLEDCommand(
                    serialBuffer
                );
            }

            else
            {
                // Otherwise it is
                // X,Y PID data

                parseData(
                    serialBuffer
                );
            }


            bufferIndex = 0;
        }


        // ----------------------------------------------------
        // NORMAL CHARACTER
        // ----------------------------------------------------

        else
        {
            if (
                bufferIndex
                <
                sizeof(serialBuffer) - 1
            )
            {
                serialBuffer[
                    bufferIndex++
                ] = c;
            }
        }
    }
}


// ============================================================
// PROCESS LED COMMAND
// ============================================================

void processLEDCommand(
    char *data
)
{
    // data examples:
    //
    // LED:BLUE
    // LED:RED
    // LED:GREEN
    // LED:OFF


    if (
        strcmp(
            data,
            "LED:BLUE"
        ) == 0
    )
    {
        setLED("BLUE");
    }


    else if (
        strcmp(
            data,
            "LED:RED"
        ) == 0
    )
    {
        setLED("RED");
    }


    else if (
        strcmp(
            data,
            "LED:GREEN"
        ) == 0
    )
    {
        setLED("GREEN");
    }


    else if (
        strcmp(
            data,
            "LED:OFF"
        ) == 0
    )
    {
        setLED("OFF");
    }
}


// ============================================================
// RGB LED CONTROL
// ============================================================

void setLED(
    String color
)
{
    // --------------------------------------------------------
    // ALL OFF FIRST
    // --------------------------------------------------------

    digitalWrite(
        RED_PIN,
        LOW
    );

    digitalWrite(
        GREEN_PIN,
        LOW
    );

    digitalWrite(
        BLUE_PIN,
        LOW
    );


    // --------------------------------------------------------
    // RED
    // --------------------------------------------------------

    if (
        color == "RED"
    )
    {
        digitalWrite(
            RED_PIN,
            HIGH
        );
    }


    // --------------------------------------------------------
    // GREEN
    // --------------------------------------------------------

    else if (
        color == "GREEN"
    )
    {
        digitalWrite(
            GREEN_PIN,
            HIGH
        );
    }


    // --------------------------------------------------------
    // BLUE
    // --------------------------------------------------------

    else if (
        color == "BLUE"
    )
    {
        digitalWrite(
            BLUE_PIN,
            HIGH
        );
    }


    // --------------------------------------------------------
    // OFF
    // --------------------------------------------------------

    else if (
        color == "OFF"
    )
    {
        // Everything already LOW
    }


    currentLED = color;
}


// ============================================================
// PARSE X,Y
// ============================================================

void parseData(
    char *data
)
{
    char *comma = strchr(
        data,
        ','
    );


    if (comma == NULL)
    {
        return;
    }


    *comma = '\0';


    errorX = atof(
        data
    );


    errorY = atof(
        comma + 1
    );
}


// ============================================================
// PID UPDATE
// ============================================================

void updatePID(
    float dt
)
{
    // ========================================================
    // X AXIS
    // ========================================================

    float outputX =
        calculateAxis(
            errorX,
            previousErrorX,
            integralX,
            filteredDerivativeX,
            Kp_X,
            Ki_X,
            Kd_X,
            DEAD_ZONE_X,
            MAX_STEP_X,
            dt
        );


    // ========================================================
    // Y AXIS
    // ========================================================

    float outputY =
        calculateAxis(
            errorY,
            previousErrorY,
            integralY,
            filteredDerivativeY,
            Kp_Y,
            Ki_Y,
            Kd_Y,
            DEAD_ZONE_Y,
            MAX_STEP_Y,
            dt
        );


    // ========================================================
    // UPDATE SERVO POSITION
    // ========================================================

    servoXPos += outputX;

    servoYPos += outputY;


    // ========================================================
    // LIMIT SERVO POSITION
    // ========================================================

    servoXPos =
        constrain(
            servoXPos,
            X_MIN,
            X_MAX
        );


    servoYPos =
        constrain(
            servoYPos,
            Y_MIN,
            Y_MAX
        );


    // ========================================================
    // WRITE SERVO
    // ========================================================

    servoX.write(
        (int)servoXPos
    );


    servoY.write(
        (int)servoYPos
    );
}


// ============================================================
// PID AXIS
// ============================================================

float calculateAxis(
    float error,
    float &previousError,
    float &integral,
    float &filteredDerivative,
    float Kp,
    float Ki,
    float Kd,
    float deadZone,
    float maxStep,
    float dt
)
{
    // --------------------------------------------------------
    // DEAD ZONE
    // --------------------------------------------------------

    if (
        abs(error)
        <= deadZone
    )
    {
        integral = 0;

        filteredDerivative = 0;

        previousError = error;

        return 0;
    }


    // --------------------------------------------------------
    // PROPORTIONAL
    // --------------------------------------------------------

    float P =
        Kp * error;


    // --------------------------------------------------------
    // INTEGRAL
    // --------------------------------------------------------

    integral +=
        error * dt;


    integral =
        constrain(
            integral,
            -500.0,
            500.0
        );


    float I =
        Ki * integral;


    // --------------------------------------------------------
    // DERIVATIVE
    // --------------------------------------------------------

    float derivative = 0;


    if (dt > 0)
    {
        derivative =
            (
                error
                -
                previousError
            )
            /
            dt;
    }


    // --------------------------------------------------------
    // FILTER DERIVATIVE
    // --------------------------------------------------------

    filteredDerivative =
        (
            DERIVATIVE_FILTER
            *
            derivative
        )
        +
        (
            (
                1.0
                -
                DERIVATIVE_FILTER
            )
            *
            filteredDerivative
        );


    float D =
        Kd
        *
        filteredDerivative;


    // --------------------------------------------------------
    // PID OUTPUT
    // --------------------------------------------------------

    float output =
        P + I + D;


    // --------------------------------------------------------
    // LIMIT MOVEMENT
    // --------------------------------------------------------

    output =
        constrain(
            output,
            -maxStep,
            maxStep
        );


    // --------------------------------------------------------
    // SAVE ERROR
    // --------------------------------------------------------

    previousError =
        error;


    return output;
}