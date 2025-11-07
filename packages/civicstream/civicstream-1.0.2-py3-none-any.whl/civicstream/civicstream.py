#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Required libraries and imports
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from datetime import datetime
import itertools, math, signal, struct, wave
import serial.tools.list_ports
import multiprocessing as mp
import numpy as np
import argparse

# Hide the Pygame support prompt
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'True'
import pygame, pygame.locals

# Device constants
DEVICE_VID = 4617
DEVICE_PID = 2829
PACKET_HEADER_BYTES = 36
AUDIO_SAMPLE_WIDTH = 2
AUDIO_SAMPLE_RATE = 48000
AUDIO_BUFFER_SAMPLES = 32000
AUDIO_NUM_BYTES_PER_CHANNEL = AUDIO_SAMPLE_RATE * AUDIO_SAMPLE_WIDTH
AUDIO_BUFFER_CHUNKS = 4 * AUDIO_SAMPLE_RATE // AUDIO_BUFFER_SAMPLES
PACKET_END_DELIMITER = b"\xFE\xF0\xF2\x25"
RESPONSE_PACKET_DELIMITER = b"\xFE\xF9"
RESPONSE_ACK_PACKET = b"\x01\x02"

# Data packet structure
class DataPacket:
  def __init__(self, audio, num_channels, timestamp, lat, lon, ht, q1, q2, q3, delimiter):
    self.audio_num_bytes = num_channels * AUDIO_NUM_BYTES_PER_CHANNEL
    self.audio = np.concatenate(np.frombuffer(audio, dtype=np.int16).reshape(AUDIO_BUFFER_CHUNKS, num_channels, -1), axis=1).tobytes()
    self.timestamp = timestamp
    self.lat = lat
    self.lon = lon
    self.ht = ht
    self.qx = q2 / 1073741824.0
    self.qy = q3 / 1073741824.0
    self.qz = -q1 / 1073741824.0
    self.qw = (1.0 - (self.qx**2 + self.qy**2 + self.qz**2))**0.5
    self.roll, self.pitch, self.yaw = self.__quat_to_roll_pitch_yaw__()
    self.delimiter = delimiter

  @staticmethod
  def _quat_mult(q1w, q1x, q1y, q1z, q2w, q2x, q2y, q2z):
    return (q1w * q2w - q1x * q2x - q1y * q2y - q1z * q2z,
            q1w * q2x + q1x * q2w + q1y * q2z - q1z * q2y,
            q1w * q2y - q1x * q2z + q1y * q2w + q1z * q2x,
            q1w * q2z + q1x * q2y - q1y * q2x + q1z * q2w)
  
  @staticmethod
  def _heading_to_direction(degrees):
    if degrees > 330.0 or degrees <= 30.0:
      return "N"
    elif 30.0 < degrees <= 60.0:
      return "NE"
    elif 60.0 < degrees <= 120.0:
      return "E"
    elif 120.0 < degrees <= 150.0:
      return "SE"
    elif 150.0 < degrees <= 210.0:
      return "S"
    elif 210.0 < degrees <= 240.0:
      return "SW"
    elif 240.0 < degrees <= 300.0:
      return "W"
    elif 300.0 < degrees <= 330.0:
      return "NW"

  def __quat_to_roll_pitch_yaw__(self):
    # If the quaternion is invalid, return zero angles
    if isinstance(self.qw, complex):
      return 0, 0, 0

    # Compute roll (x-axis rotation)
    t0 = self.qw * self.qx + self.qy * self.qz
    t1 = 0.5 - (self.qx * self.qx + self.qy * self.qy)
    roll = math.atan2(t0, t1) * 180.0 / math.pi

    # Compute pitch (y-axis rotation)
    t2 = 2.0 * (self.qw * self.qy - self.qx * self.qz)
    t2 = max(-1.0, min(1.0, t2))
    pitch = math.asin(t2) * 180.0 / math.pi

    # Compute yaw (z-axis rotation)
    t3 = self.qw * self.qz + self.qx * self.qy
    t4 = 0.5 - (self.qy * self.qy + self.qz * self.qz)
    yaw = math.atan2(t3, t4) * 180.0 / math.pi
    #return roll, yaw, pitch
    return -(90.0 + roll), pitch, (yaw - 90.0) % 360.0

  def to_bytes(self):
    return struct.pack(f"<{self.audio_num_bytes}sdfffiii4s", self.audio, self.timestamp, self.lat, self.lon, self.ht, self.q1, self.q2, self.q3, self.delimiter)

  def __str__(self):
    time_string = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return f"\n------------------------- {time_string} -------------------------\n" \
           f"Audio: {len(self.audio)} samples\n" \
           f"Timestamp: {self.timestamp}\n" \
           f"Location: <{self.lat}, {self.lon}, {self.ht}>\n" \
           f"Orientation (Quaternions): <{self.qw}, {self.qx}, {self.qy}, {self.qz}>\n" \
           f"Orientation (Roll/Pitch/Yaw): <{self.roll}, {self.pitch}, {self.yaw}>\n"

  def __repr__(self):
    return self.__str__()

  @staticmethod
  def from_bytes(data, num_channels):
    audio_num_bytes = num_channels * AUDIO_NUM_BYTES_PER_CHANNEL
    unpacked_data = struct.unpack("<dfffiii4s", data[audio_num_bytes:])
    return DataPacket(data[:audio_num_bytes], num_channels, *unpacked_data)


# Visualizer class to handle IMU graphics rendering
class ImuVisualizer:
  def __init__(self):
      print("Initializing graphics libraries...")
      pygame.init()
      pygame.display.set_mode((640, 480), pygame.locals.OPENGL | pygame.locals.DOUBLEBUF)
      pygame.display.set_caption("CivicAlert Orientation Visualizer")
      glViewport(0, 0, 640, 480)
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()
      gluPerspective(45, 1.0*640/480, 0.1, 100.0)
      glMatrixMode(GL_MODELVIEW)
      glLoadIdentity()
      glShadeModel(GL_SMOOTH)
      glClearColor(0.0, 0.0, 0.0, 0.0)
      glClearDepth(1.0)
      glEnable(GL_DEPTH_TEST)
      glDepthFunc(GL_LEQUAL)
      glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

  def __draw_text__(self, position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

  def update(self, yaw, pitch, roll, qw, qx, qy, qz):
    pygame.event.poll()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)
    self.__draw_text__((-2.6, 1.8, 2), "CivicAlert Orientation", 18)
    self.__draw_text__((-2.6, 1.6, 2), f"Heading: {int(yaw)}\N{DEGREE SIGN} ({DataPacket._heading_to_direction(yaw)}), Tilt: {int(pitch)}\N{DEGREE SIGN}", 16)
    self.__draw_text__((-2.6, -1.9, 2), f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}", 16)
    glRotatef(2 * math.acos(qw) * 180.00 / math.pi, qz, qy, qx)

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()
    pygame.display.flip()


# Helper function to interleave non-interleaved audio data
def interleave_audio(audio_data, num_channels):
  audio_num_bytes = num_channels * AUDIO_NUM_BYTES_PER_CHANNEL
  ch_data = [np.frombuffer(audio_data[i:i+AUDIO_NUM_BYTES_PER_CHANNEL], dtype=np.int16)
            for i in range(0, audio_num_bytes, AUDIO_NUM_BYTES_PER_CHANNEL)]
  return np.array(list(itertools.chain(*zip(*ch_data)))).tobytes()

# Helper function to write audio to the disk in a separate process
def write_audio(io_queue, num_channels):

  # Ignore signals so that parent process can handle them
  signal.signal(signal.SIGINT, signal.SIG_IGN)

  # Create a new wave file to save the audio data
  now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  with wave.open(f"civicalert-{now}.wav", "wb") as wav_file:
    wav_file.setnchannels(num_channels)
    wav_file.setsampwidth(AUDIO_SAMPLE_WIDTH)
    wav_file.setframerate(AUDIO_SAMPLE_RATE)

    # Loop forever waiting for audio data
    audio_data = io_queue.get()
    while audio_data is not None:
      wav_file.writeframes(interleave_audio(audio_data, num_channels))
      audio_data = io_queue.get()


# Main program loop
def main_loop(visualize_imu, num_channels):

  # Search for a CivicAlert device
  device = None
  for port in serial.tools.list_ports.comports():
    if port.vid == DEVICE_VID and port.pid == DEVICE_PID:
      print(f"CivicAlert device found on {port.device}")
      device = port.device
      break
  if device is None:
    print("CivicAlert device not found")
    exit(1)
  
  # Spawn a new process to handle disk IO
  mp.set_start_method("spawn")
  io_queue = mp.Queue()
  io_process = mp.Process(target=write_audio, args=(io_queue, num_channels))
  io_process.start()

  # Initialize the IMU visualizer if requested
  imu_visualizer = ImuVisualizer() if visualize_imu else None

  # Initiate a connection to the device
  try:
    print("Connecting to the CivicAlert device...")
    with serial.Serial(device) as ser:
      print("Successfully connected to the device!")
      packet_size_bytes = PACKET_HEADER_BYTES + (num_channels * AUDIO_NUM_BYTES_PER_CHANNEL)

      # Search for consecutive packet-ending delimiters
      print("Awaiting packet synchronization...")
      while True:
        data = ser.read(2 * packet_size_bytes)
        idx = data.find(PACKET_END_DELIMITER)
        if idx > -1:
          data = ser.read(idx + len(PACKET_END_DELIMITER))
          if data[-len(PACKET_END_DELIMITER):] == PACKET_END_DELIMITER:
            break
      print("Packet synchronization complete! Starting data capture...")

      # Loop forever reading data from the device
      while True:

        # Read the packet data
        data = ser.read(packet_size_bytes)
        ser.write(RESPONSE_PACKET_DELIMITER + RESPONSE_ACK_PACKET)

        # Append the received audio to the WAV file and print the packet
        packet = DataPacket.from_bytes(data, num_channels)
        if packet.delimiter != PACKET_END_DELIMITER:
          break
        io_queue.put(packet.audio)
        if imu_visualizer:
          imu_visualizer.update(packet.yaw, packet.pitch, packet.roll, packet.qw, packet.qx, packet.qy, packet.qz)
        print(packet)

  # Handle errors and exceptions
  except serial.SerialException as e:
    print(f"\nError communicating with the device: {e}")
    print("\nExiting...")
  except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Exiting...")

  # Shut down the IO data handling process
  io_queue.put(None)
  io_process.join()


# Application entry point
def main():

  # Parse command line arguments and start the main loop
  parser = argparse.ArgumentParser(description="CivicAlert Streaming Data Capture and Visualization Tool")
  parser.add_argument("-i", "--imu", help="visualize streaming IMU data", default=False, action='store_true')
  parser.add_argument("-c", "--channels", help="number of channels", default=4, type=int)
  args = parser.parse_args()
  main_loop(args.imu, args.channels)
  pygame.quit()

if __name__ == '__main__':
  main()
