// api.test.js
import axios from 'axios';
import { getToken, signUp, storeToken } from '../api/loginHandler';
import { getApplications } from '../api/applicationHandler';
import fetch from '../api/handler';

// Mock axios
jest.mock('axios');

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

global.localStorage = localStorageMock;

describe('API Handlers', () => {
  // Reset mocks before each test
  beforeEach(() => {
    axios.mockReset();
    localStorageMock.getItem.mockReset();
    localStorageMock.setItem.mockReset();
    localStorageMock.removeItem.mockReset();
  });

  // Test 1: Base fetch handler with successful response
  test('fetch handler resolves with response data on success', async () => {
    const mockData = { success: true, data: 'test-data' };
    axios.mockResolvedValueOnce({ data: mockData });

    const options = {
      method: 'GET',
      url: '/test-endpoint'
    };

    const result = await fetch(options);
    
    expect(axios).toHaveBeenCalledWith({
      url: 'http://127.0.0.1:5000/test-endpoint',
      method: 'GET',
      headers: undefined,
      params: undefined,
      data: undefined
    });
    
    expect(result).toEqual(mockData);
  });

  // Test 2: Base fetch handler with error response
  test('fetch handler rejects with error', async () => {
    const error = new Error('Network error');
    error.status = 500;
    axios.mockRejectedValueOnce(error);

    const options = {
      method: 'GET',
      url: '/test-endpoint'
    };

    await expect(fetch(options)).rejects.toThrow('Network error');
  });

  // Test 3: Base fetch handler with unauthorized error
  test('fetch handler redirects to homepage on 401 response', async () => {
    const error = new Error('Unauthorized');
    error.status = 401;
    axios.mockRejectedValueOnce(error);

    const options = {
      method: 'GET',
      url: '/test-endpoint'
    };

    try {
      await fetch(options);
    } catch (e) {
      // Ignore the error
    }

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
  });

  // Test 4: Login handler
  test('getToken calls the login endpoint with credentials', async () => {
    const credentials = { username: 'testuser', password: 'password' };
    const mockResponse = { token: 'test-token', expiry: '01/01/2025' };
    
    axios.mockResolvedValueOnce({ data: mockResponse });

    const result = await getToken(credentials);
    
    expect(axios).toHaveBeenCalledWith({
      url: 'http://127.0.0.1:5000/users/login',
      method: 'POST',
      headers: undefined,
      params: undefined,
      data: credentials
    });
    
    expect(result).toEqual(mockResponse);
  });

  // Test 5: Signup handler
  test('signUp calls the signup endpoint with user data', async () => {
    const userData = { 
      username: 'testuser', 
      password: 'password',
      fullName: 'Test User' 
    };
    const mockResponse = { id: 123, username: 'testuser', fullName: 'Test User' };
    
    axios.mockResolvedValueOnce({ data: mockResponse });

    const result = await signUp(userData);
    
    expect(axios).toHaveBeenCalledWith({
      url: 'http://127.0.0.1:5000/users/signup',
      method: 'POST',
      headers: undefined,
      params: undefined,
      data: userData
    });
    
    expect(result).toEqual(mockResponse);
  });

  // Test 6: Store token function
  test('storeToken saves authentication data to localStorage', () => {
    const authData = {
      token: 'test-token',
      expiry: '01/01/2025',
      userId: '123',
      profile: {
        fullName: 'Test User',
        username: 'testuser',
        skills: ['JavaScript', 'React'],
        job_levels: ['Entry'],
        locations: ['Remote'],
        institution: 'Test University',
        phone_number: '123-456-7890',
        address: '123 Test St',
        email: 'test@example.com'
      }
    };

    storeToken(authData);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('expiry', '01/01/2025');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('userId', '123');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('userProfile', expect.any(String));
    
    // Verify the profile JSON
    const profileJSON = localStorageMock.setItem.mock.calls.find(
      call => call[0] === 'userProfile'
    )[1];
    
    const profileData = JSON.parse(profileJSON);
    expect(profileData.skills).toEqual(['JavaScript', 'React']);
    expect(profileData.fullName).toEqual('Test User');
  });

  // Test 7: Store token handles missing profile
  test('storeToken handles missing profile data', () => {
    const authData = {
      token: 'test-token',
      expiry: '01/01/2025',
      userId: '123'
      // No profile data
    };

    storeToken(authData);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('expiry', '01/01/2025');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('userId', '123');
    
    // Verify userProfile wasn't set
    const profileSetCall = localStorageMock.setItem.mock.calls.find(
      call => call[0] === 'userProfile'
    );
    expect(profileSetCall).toBeUndefined();
  });

  // Test 8: Store token handles missing token
  test('storeToken handles missing token', () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const authData = {
      // No token
      expiry: '01/01/2025',
      userId: '123'
    };

    storeToken(authData);
    
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    expect(consoleErrorSpy).toHaveBeenCalled();
    
    consoleErrorSpy.mockRestore();
  });

  // Test 9: Get applications handler
  test('getApplications calls the applications endpoint with auth header', async () => {
    const mockToken = 'test-token';
    localStorageMock.getItem.mockReturnValueOnce(mockToken);
    
    const mockApplications = [
      { id: 1, jobTitle: 'Software Engineer', companyName: 'Google' },
      { id: 2, jobTitle: 'Data Scientist', companyName: 'Microsoft' }
    ];
    
    axios.mockResolvedValueOnce({ data: mockApplications });

    const result = await getApplications();
    
    expect(axios).toHaveBeenCalledWith({
      url: 'http://127.0.0.1:5000/applications',
      method: 'GET',
      headers: {
        Authorization: 'Bearer test-token'
      },
      params: undefined,
      data: undefined
    });
    
    expect(result).toEqual(mockApplications);
  });

  // Test 10: Fetch with all parameters
  test('fetch handler includes all parameters in the request', async () => {
    const mockData = { success: true };
    axios.mockResolvedValueOnce({ data: mockData });

    const options = {
      method: 'POST',
      url: '/test-endpoint',
      headers: { 'Content-Type': 'application/json' },
      params: { query: 'test' },
      body: { data: 'test-data' }
    };

    await fetch(options);
    
    expect(axios).toHaveBeenCalledWith({
      url: 'http://127.0.0.1:5000/test-endpoint',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      params: { query: 'test' },
      data: { data: 'test-data' }
    });
  });
});