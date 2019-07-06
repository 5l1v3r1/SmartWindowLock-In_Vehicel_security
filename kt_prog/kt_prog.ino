// Kribo Tech

// control system
/* --> bridge between main system to arduino using the serial communicatoin

   --> connect arduino to the main system via system cable (USB -A)
*/


#include <Servo.h>
#include <SoftwareSerial.h>


#ifndef time_delay
#define time_delay 100
#define servo_1 3
#define servo_2 4
#define servo_3 5
#define servo_4 6
#define ult1_echo 7
#define ult1_trig 8
#define ult2_echo 9
#define ult2_trig 10
#define indic_led 13
#define servo_init_pos 0
#define servo_end_pos 90
#define servo_delay 15
#endif

float ult_calc1(int,int);
float ult_calc2(int,int);
void pin_def();
void servo_init(int,int,int,int);
void servo_init_state();
void servo_end_state();

struct calc{
  float distance;
  long duration;
  long r_c;
};

// Servo definition
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

float td_1,td_2;
String Serial_read;

void pin_def()
{
  pinMode(indic_led, OUTPUT);
  pinMode(ult1_echo, INPUT);
  pinMode(ult2_echo, INPUT);
  pinMode(ult1_trig, OUTPUT);
  pinMode(ult2_trig, OUTPUT);

}

void servo_init(int s1,int s2,int s3,int s4)
{
  servo1.attach(s1);
  servo2.attach(s1);
  servo3.attach(s1);
  servo4.attach(s1);
}

void servo_init_state()
{
  servo1.write(servo_init_pos);
  servo2.write(servo_init_pos);
  servo3.write(servo_init_pos);
  servo4.write(servo_init_pos);
}
void servo_end_state()
{
  servo1.write(servo_end_pos);
  servo2.write(servo_end_pos);
  servo3.write(servo_end_pos);
  servo4.write(servo_end_pos);
}

float ult_calc1(int echo_port,int trig_port)
{
  calc u1;
  digitalWrite(trig_port, LOW);
  digitalWrite(trig_port, HIGH);
  delayMicroseconds(100);
  digitalWrite(trig_port, LOW);
  u1.duration=pulseIn(echo_port, HIGH);
  u1.r_c=3.4*u1.duration/2;
  u1.distance=u1.r_c/100.00;

  /*Serial.print("Duration 1 :");
  Serial.print(u1.duration);
  Serial.print("\n");
*/
  //Serial.print("Distance 1 :");
  if (u1.duration > 38000)
  {
    Serial.println("System out of range");
    digitalWrite(indic_led, HIGH);   // led blinks 100ms for ultrasonic 1 error
    delay(time_delay);
    digitalWrite(indic_led, LOW);
    delay(time_delay);
  }
  //else Serial.print(u1.distance);
  //Serial.print("\n");

  delay(time_delay);

  return u1.distance;

}

float ult_calc2(int echo_port,int trig_port)
{
  calc u2;
  digitalWrite(trig_port, LOW);
  digitalWrite(trig_port, HIGH);
  delayMicroseconds(100);
  digitalWrite(ult2_trig, LOW);
  u2.duration=pulseIn(echo_port, HIGH);
  u2.r_c=3.4*u2.duration/2;
  u2.distance=u2.r_c/100.00;

  /*Serial.print("Duration 2 :");
  Serial.print(u2.duration);
  Serial.print("\n");

  Serial.print("Distance 2 :");*/

  if (u2.duration > 38000)
  {
    Serial.println("System out of range");
    digitalWrite(indic_led, HIGH);  // led blinks 500ms for ultrasonic 1 error
    delay(500);
    digitalWrite(indic_led, LOW);
    delay(500);
  }
  //else Serial.print(u1.distance);
  //Serial.print("\n");

  delay(time_delay);

  return u2.distance;


}


void setup()
{
  Serial.begin(115200);
  Serial.println("[info .. ] system started to initialise");
  Serial.println("[info .. ] motors started started to initialise");
  pin_def();
  servo_init(servo_1,servo_2,servo_3,servo_4);
  Serial.print("[info .. ] system initialise done ...");
  Serial.print("If you need to check the system working uncomment all the serial part in the program");
  Serial.print("\n");
  Serial.print("while system working comment all the uncommented lines");
  Serial.print("\n");
}

void loop()
{
  while (!Serial.available());

  if (Serial.available())
  {
  Serial_read = Serial.readString();
  }

  /*Serial.print("[Serial Data { } .. ]");
  Serial.print(Serial_read);
  Serial.print("\n");
*/

  td_1=ult_calc1(ult1_echo,ult1_trig);
  td_2=ult_calc2(ult2_echo,ult2_trig);


  if (Serial_read == "a") // process after the object is detected ; a --> center point detection
  {
    if (td_1 <= 100) // change to the respective values
    {
    servo1.write(servo_init_pos); // for left side
    servo2.write(servo_init_pos);
    }
    else if (td_2 <=100) // change to the respective values
    {
      servo3.write(servo_init_pos); // for right side
      servo4.write(servo_init_pos);
    }
    else
    {
      servo_end_state();
    }
  }

  else if ((td_1 <= 100) && (Serial_read == "l")) // change to the respective values ; l --> left point detection
  {
  servo1.write(servo_init_pos); // for left side
  servo2.write(servo_init_pos);
  }
  else if ((td_2 <=100) && (Serial_read == "r")) // change to the respective values ; r --> right point detection
  {
    servo3.write(servo_init_pos); // for right side
    servo4.write(servo_init_pos);
  }

  else if (Serial_read == "e") servo_init_state(); // on main System exit

  else servo_init_state();  // default


  Serial_read = "0";

  delay(100);

}
