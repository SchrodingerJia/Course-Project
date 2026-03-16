/*
 * Copyright (c) 2021, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
#include "board.h"
#include <stdio.h>
#include "oled.h"
#include "ti_msp_dl_config.h"
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

char* morse_table[36] = {
    // 0-9
    "11111", // 0
    "01111", // 1
    "00111", // 2
    "00011", // 3
    "00001", // 4
    "00000", // 5
    "10000", // 6
    "11000", // 7
    "11100", // 8
    "11110", // 9
    
    // a-z
    "01",    // a
    "1000",  // b
    "1010",  // c
    "100",   // d
    "0",     // e
    "0010",  // f
    "110",   // g
    "0000",  // h
    "00",    // i
    "0111",  // j
    "101",   // k
    "0100",  // l
    "11",    // m
    "10",    // n
    "111",   // o
    "0110",  // p
    "1101",  // q
    "010",   // r
    "000",   // s
    "1",     // t
    "001",   // u
    "0001",  // v
    "011",   // w
    "1001",  // x
    "1011",  // y
    "1100"   // z
};

int char2index(char c) {
	if(isdigit(c)) return c - '0';
	else if (islower(c)) return c - 'a' + 10;
	else return -1;
}

void dot(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	DL_GPIO_setPins(PORT, pins);
	delay_ms(duration);
	DL_GPIO_clearPins(PORT, pins);
}

void dash(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	DL_GPIO_setPins(PORT, pins);
	delay_ms(duration * 3);
	DL_GPIO_clearPins(PORT, pins);
}

void sep(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	DL_GPIO_clearPins(PORT, pins);
	delay_ms(duration);
	DL_GPIO_clearPins(PORT, pins);
}

void char_sep(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	DL_GPIO_clearPins(PORT, pins);
	delay_ms(duration * 3);
	DL_GPIO_clearPins(PORT, pins);
}

void word_sep(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	DL_GPIO_clearPins(PORT, pins);
	delay_ms(duration * 7);
	DL_GPIO_clearPins(PORT, pins);
}

void start_signal(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	// _._._
	DL_GPIO_clearPins(PORT, pins);
	dash(PORT, pins, duration);
	sep(PORT, pins, duration);
	dot(PORT, pins, duration);
	sep(PORT, pins, duration);
	dash(PORT, pins, duration);
	sep(PORT, pins, duration);
	dot(PORT, pins, duration);
	sep(PORT, pins, duration);
	dash(PORT, pins, duration);
	char_sep(PORT, pins, duration);
	DL_GPIO_clearPins(PORT, pins);
}

void end_signal(GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	// ..._.
	DL_GPIO_clearPins(PORT, pins);
	dot(PORT, pins, duration);
	sep(PORT, pins, duration);
	dot(PORT, pins, duration);
	sep(PORT, pins, duration);
	dot(PORT, pins, duration);
	sep(PORT, pins, duration);
	dash(PORT, pins, duration);
	sep(PORT, pins, duration);
	dot(PORT, pins, duration);
	DL_GPIO_clearPins(PORT, pins);
}

void string2control(const char* string, GPIO_Regs *PORT, uint32_t pins, unsigned int duration) {
	unsigned int len = strlen(string);
	int i = 0;
	while(string[i] != '\0') {
		int j = 0;
		char* morse = morse_table[char2index(string[i])];
		while(morse[j] != '\0') {
			switch (morse[j]) {
				case '0'  : {dot(PORT, pins, duration); break;}
				case '1'  : {dash(PORT, pins, duration); break;}
			}
			sep(PORT, pins, duration);
			j++;
		}
		char_sep(PORT, pins, duration);
		i++;
	}
}

void morse_cycle(const char* string, GPIO_Regs *PORT, uint32_t pins, unsigned int duration, unsigned int gap) {
	start_signal(PORT, pins, duration);
	string2control(string, PORT, pins, duration);
	end_signal(PORT, pins, duration);
	delay_ms(gap);
}

int main(void)
{
    board_init();
    OLED_Init();
    OLED_Clear();
	SYSCFG_DL_init();

	// Define constants
	const int CONFIG_ACTIVITY = 0;
	const int SEND_ACTIVITY = 1;
	const int STRING_PAGE = 0;
	const int DURATION_PAGE = 1;
	const int INTERVAL_PAGE = 2;
	const int PREV_KEY = 1;
	const int ENTER_KEY = 2;
	const int NEXT_KEY = 3;
	const int DELETE_KEY = 4;
	
    int INFO_i = 0;
	int Duration_i = 0;
	int Time_Interval_i = 0;

	int INFO_j = 0;
	int Duration_j = 0;
	int Time_Interval_j = 0;
	
	int key = 0;
	int mode = 0;
	int work_mode = 0;
	
	char INFO_modle_string[36] = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9'};
	char Num_modle_string[10]={'0','1','2','3','4','5','6','7','8','9'};
		
	char INFO_string[20]="";
	char Duration_string[20]="200";
	char Time_Interval_string[20]="2000";
		
	char Storage_INFO[20]="sos";
	int  Storage_Duration=200;
	int  Storage_Time_Interval=2000;

	OLED_Refresh();

	while(1) 
    {
		// Switch Activity
		if(DL_GPIO_readPins(GPIOB,DL_GPIO_PIN_8)>0)
		{
			work_mode++;							
		}
		
		// Setting Configs
		if(work_mode%2==CONFIG_ACTIVITY)
		{		
			OLED_ShowString(0,52,(uint8_t *) "Setting    ",8,1);
			// Confirm Setting
			if(DL_GPIO_readPins(KEYS_PORT,KEYS_PIN2_PIN)>0)
				{
					if(mode%3==STRING_PAGE)	// Confirm String Setting
					{
						INFO_string[INFO_j]='\0';
						strcpy(Storage_INFO, INFO_string);
						INFO_i = 0;
						INFO_j = 0;
					}
					else if(mode%3==DURATION_PAGE)	// Confirm Duration Setting
					{
						Storage_Duration = atoi(Duration_string);
						Duration_i = 0;
						Duration_j = 0;
					}
					else if(mode%3==INTERVAL_PAGE)	// Confirm Interval Setting
					{
						Storage_Time_Interval = atoi(Time_Interval_string);
						Time_Interval_i = 0;
						Time_Interval_j = 0;
					}
					mode++;
					OLED_Clear();
				}

			// Setting Pages
			if		(DL_GPIO_readPins(GPIOB,DL_GPIO_PIN_3)>0) key = 1;
			else if	(DL_GPIO_readPins(GPIOB,DL_GPIO_PIN_6)>0) key = 2;
			else if	(DL_GPIO_readPins(GPIOB,DL_GPIO_PIN_7)>0) key = 3;
			else if	(DL_GPIO_readPins(GPIOB,DL_GPIO_PIN_18)>0) key = 4;				

			if(mode%3==STRING_PAGE)	// String Setting Page
			{
				OLED_ShowString(0,0,(uint8_t *) "INFO:",16,1);
				OLED_ShowString(40,0,(uint8_t *) Storage_INFO,16,1);
				OLED_ShowChar(0,36,(uint8_t) INFO_modle_string[INFO_i],16,1);
						
				if(key == 1)		// Prev
				{	
					if(INFO_i>0)	INFO_i--;
					OLED_ShowChar(0,36,(uint8_t) INFO_modle_string[INFO_i],16,1);			
				}
				
				else if(key == 2)	// Enter
				{	
					INFO_string[INFO_j]=INFO_modle_string[INFO_i];
					OLED_ShowChar(INFO_j *8,20,(uint8_t) INFO_string[INFO_j],16,1);
					INFO_j ++;
				}			

				else if(key == 3)	// Next
				{	
					if(INFO_i<36)	INFO_i++;
					OLED_ShowChar(0,36,(uint8_t) INFO_modle_string[INFO_i],16,1);						
				}			

				else if(key == 4)	// Delete
				{	
					OLED_PartClear(INFO_j *8-10,26,INFO_j *8-2,29);
					INFO_j --;
				}		

				OLED_Refresh();	
				key = 0;
				delay_ms(200);	
			}

			else if(mode%3==DURATION_PAGE)	// Duration Setting Page
			{
						
				OLED_ShowString(0,0,(uint8_t *) "Duration:",16,1);
				OLED_ShowString(72,0,(uint8_t *) Duration_string,16,1);
				OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Duration_i],16,1);
				
				if(key == 1)		// Prev
				{	
					if(Duration_i>0)	Duration_i--;
					OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Duration_i],16,1);
				}

				else if(key == 2)	// Enter
				{	
					Duration_string[Duration_j]= Num_modle_string[Duration_i];
					OLED_ShowChar(Duration_j*8,20,(uint8_t) Duration_string[Duration_j],16,1);
					Duration_j++;
				}			

				else if(key == 3)	// Next
				{	
					if(Duration_i<10)	Duration_i++;
					OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Duration_i],16,1);	
				}			

				else if(key == 4)	// Delete
				{	
					OLED_PartClear(Duration_j*8-10,26,Duration_j*8-2,29);
					Duration_j--;
				}			

				OLED_Refresh();	
				key = 0;
				delay_ms(200);	
			}

			else if(mode%3==INTERVAL_PAGE)	// Interval Setting Page
			{
						
				OLED_ShowString(0,0,(uint8_t *) "GAP:",16,1);
				OLED_ShowString(40,0,(uint8_t *) Time_Interval_string,16,1);
				OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Time_Interval_i],16,1);
						
				if(key == 1)		// Prev
				{	
					if(Time_Interval_i>0) Time_Interval_i--;
					OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Time_Interval_i],16,1);		
				}

				else if(key == 2)	// Enter
				{	
					Time_Interval_string[Time_Interval_j]=Num_modle_string[Time_Interval_i];
					OLED_ShowChar(Time_Interval_j*8,20,(uint8_t) Time_Interval_string[Time_Interval_j],16,1);
					Time_Interval_j++;
				}			

				else if(key == 3)	// Next
				{	
					if(Time_Interval_i<10) Time_Interval_i++;
					OLED_ShowChar(0,36,(uint8_t) Num_modle_string[Time_Interval_i],16,1);	
				}			

				else if(key == 4)	// Delete
				{	
					OLED_PartClear(Time_Interval_j*8-10,26,Time_Interval_j*8-2,29);
					Time_Interval_j--;
				}		

				OLED_Refresh();	
				key = 0;
				delay_ms(200);	
			}
		}
		
		// Sending Morse Code
		else if(work_mode%2==SEND_ACTIVITY)	
		{
			OLED_ShowString(0,52,(uint8_t *)"Successful",8,1);
			OLED_Refresh();	
			morse_cycle(Storage_INFO, GPIOB, DL_GPIO_PIN_20,Storage_Duration, Storage_Time_Interval);
		}		
    }
}