import { describe, it, expect } from 'vitest';
import { 
  validateJSON, 
  formatJSON, 
  compressJSON, 
  safeJSONParse, 
  safeJSONStringify,
  extractJSONPath,
  mergeJSONObjects 
} from './jsonUtils';

describe('JSON Utils', () => {
  describe('validateJSON', () => {
    it('should validate valid JSON strings', () => {
      expect(validateJSON('{"key": "value"}')).toBe(true);
      expect(validateJSON('[]')).toBe(true);
      expect(validateJSON('null')).toBe(true);
      expect(validateJSON('true')).toBe(true);
      expect(validateJSON('123')).toBe(true);
      expect(validateJSON('"string"')).toBe(true);
    });

    it('should reject invalid JSON strings', () => {
      expect(validateJSON('{"key": value}')).toBe(false);
      expect(validateJSON('{')).toBe(false);
      expect(validateJSON('undefined')).toBe(false);
      expect(validateJSON('function(){}')).toBe(false);
      expect(validateJSON('')).toBe(false);
    });

    it('should handle null and undefined inputs', () => {
      expect(validateJSON(null)).toBe(false);
      expect(validateJSON(undefined)).toBe(false);
    });
  });

  describe('formatJSON', () => {
    it('should format JSON with proper indentation', () => {
      const input = '{"name":"John","age":30,"city":"New York"}';
      const expected = '{\n  "name": "John",\n  "age": 30,\n  "city": "New York"\n}';
      expect(formatJSON(input)).toBe(expected);
    });

    it('should handle arrays', () => {
      const input = '[1,2,3]';
      const expected = '[\n  1,\n  2,\n  3\n]';
      expect(formatJSON(input)).toBe(expected);
    });

    it('should return original string if JSON is invalid', () => {
      const input = '{"invalid": json}';
      expect(formatJSON(input)).toBe(input);
    });

    it('should handle nested objects', () => {
      const input = '{"user":{"name":"John","details":{"age":30}}}';
      const result = formatJSON(input);
      expect(result).toContain('  "user": {');
      expect(result).toContain('    "name": "John"');
      expect(result).toContain('    "details": {');
      expect(result).toContain('      "age": 30');
    });
  });

  describe('compressJSON', () => {
    it('should compress JSON by removing whitespace', () => {
      const input = '{\n  "name": "John",\n  "age": 30\n}';
      const expected = '{"name":"John","age":30}';
      expect(compressJSON(input)).toBe(expected);
    });

    it('should handle already compressed JSON', () => {
      const input = '{"name":"John","age":30}';
      expect(compressJSON(input)).toBe(input);
    });

    it('should return original string if JSON is invalid', () => {
      const input = '{"invalid": json}';
      expect(compressJSON(input)).toBe(input);
    });

    it('should handle arrays', () => {
      const input = '[\n  1,\n  2,\n  3\n]';
      const expected = '[1,2,3]';
      expect(compressJSON(input)).toBe(expected);
    });
  });

  describe('safeJSONParse', () => {
    it('should parse valid JSON strings', () => {
      expect(safeJSONParse('{"key": "value"}')).toEqual({ key: 'value' });
      expect(safeJSONParse('[1, 2, 3]')).toEqual([1, 2, 3]);
      expect(safeJSONParse('null')).toBeNull();
      expect(safeJSONParse('true')).toBe(true);
      expect(safeJSONParse('123')).toBe(123);
    });

    it('should return null for invalid JSON', () => {
      expect(safeJSONParse('{"invalid": json}')).toBeNull();
      expect(safeJSONParse('undefined')).toBeNull();
      expect(safeJSONParse('')).toBeNull();
    });

    it('should return default value for invalid JSON', () => {
      const defaultValue = { default: true };
      expect(safeJSONParse('{"invalid": json}', defaultValue)).toEqual(defaultValue);
    });

    it('should handle null and undefined inputs', () => {
      expect(safeJSONParse(null)).toBeNull();
      expect(safeJSONParse(undefined)).toBeNull();
    });
  });

  describe('safeJSONStringify', () => {
    it('should stringify valid objects', () => {
      expect(safeJSONStringify({ key: 'value' })).toBe('{"key":"value"}');
      expect(safeJSONStringify([1, 2, 3])).toBe('[1,2,3]');
      expect(safeJSONStringify(null)).toBe('null');
      expect(safeJSONStringify(true)).toBe('true');
      expect(safeJSONStringify(123)).toBe('123');
    });

    it('should handle circular references', () => {
      const obj = { name: 'test' };
      obj.self = obj;
      const result = safeJSONStringify(obj);
      expect(result).toBe('{"name":"test","self":"[Circular]"}');
    });

    it('should handle functions', () => {
      const obj = { 
        name: 'test', 
        fn: function() { return 'hello'; }
      };
      const result = safeJSONStringify(obj);
      expect(result).toBe('{"name":"test","fn":"[Function]"}');
    });

    it('should handle undefined values', () => {
      const obj = { 
        name: 'test', 
        value: undefined 
      };
      const result = safeJSONStringify(obj);
      expect(result).toBe('{"name":"test","value":"[Undefined]"}');
    });

    it('should handle symbols', () => {
      const obj = { 
        name: 'test', 
        symbol: Symbol('test') 
      };
      const result = safeJSONStringify(obj);
      expect(result).toBe('{"name":"test","symbol":"[Symbol]"}');
    });

    it('should return null for unstringifiable values', () => {
      // Create an object that will throw during stringification
      const obj = {};
      Object.defineProperty(obj, 'problematic', {
        get: function() { throw new Error('Cannot access this property'); }
      });
      
      expect(safeJSONStringify(obj)).toBeNull();
    });
  });

  describe('extractJSONPath', () => {
    const testObject = {
      user: {
        name: 'John',
        age: 30,
        address: {
          street: '123 Main St',
          city: 'New York'
        }
      },
      items: [
        { id: 1, name: 'Item 1' },
        { id: 2, name: 'Item 2' }
      ]
    };

    it('should extract values from simple paths', () => {
      expect(extractJSONPath(testObject, 'user.name')).toBe('John');
      expect(extractJSONPath(testObject, 'user.age')).toBe(30);
    });

    it('should extract values from nested paths', () => {
      expect(extractJSONPath(testObject, 'user.address.street')).toBe('123 Main St');
      expect(extractJSONPath(testObject, 'user.address.city')).toBe('New York');
    });

    it('should extract values from array paths', () => {
      expect(extractJSONPath(testObject, 'items.0.name')).toBe('Item 1');
      expect(extractJSONPath(testObject, 'items.1.id')).toBe(2);
    });

    it('should return null for non-existent paths', () => {
      expect(extractJSONPath(testObject, 'user.nonexistent')).toBeNull();
      expect(extractJSONPath(testObject, 'nonexistent.path')).toBeNull();
      expect(extractJSONPath(testObject, 'items.5.name')).toBeNull();
    });

    it('should handle empty paths', () => {
      expect(extractJSONPath(testObject, '')).toEqual(testObject);
      expect(extractJSONPath(testObject, null)).toEqual(testObject);
      expect(extractJSONPath(testObject, undefined)).toEqual(testObject);
    });

    it('should handle null/undefined objects', () => {
      expect(extractJSONPath(null, 'user.name')).toBeNull();
      expect(extractJSONPath(undefined, 'user.name')).toBeNull();
    });

    it('should handle array indices as strings', () => {
      expect(extractJSONPath(testObject, 'items.0')).toEqual({ id: 1, name: 'Item 1' });
    });
  });

  describe('mergeJSONObjects', () => {
    it('should merge simple objects', () => {
      const obj1 = { a: 1, b: 2 };
      const obj2 = { c: 3, d: 4 };
      const result = mergeJSONObjects(obj1, obj2);
      expect(result).toEqual({ a: 1, b: 2, c: 3, d: 4 });
    });

    it('should override values from first object with second', () => {
      const obj1 = { a: 1, b: 2 };
      const obj2 = { b: 3, c: 4 };
      const result = mergeJSONObjects(obj1, obj2);
      expect(result).toEqual({ a: 1, b: 3, c: 4 });
    });

    it('should handle nested objects', () => {
      const obj1 = { 
        user: { name: 'John', age: 30 },
        settings: { theme: 'dark' }
      };
      const obj2 = { 
        user: { age: 31, city: 'New York' },
        settings: { language: 'en' }
      };
      const result = mergeJSONObjects(obj1, obj2);
      expect(result).toEqual({
        user: { name: 'John', age: 31, city: 'New York' },
        settings: { theme: 'dark', language: 'en' }
      });
    });

    it('should handle null/undefined inputs', () => {
      const obj = { a: 1, b: 2 };
      expect(mergeJSONObjects(null, obj)).toEqual(obj);
      expect(mergeJSONObjects(obj, null)).toEqual(obj);
      expect(mergeJSONObjects(null, null)).toEqual({});
      expect(mergeJSONObjects(undefined, obj)).toEqual(obj);
    });

    it('should handle arrays', () => {
      const obj1 = { items: [1, 2, 3] };
      const obj2 = { items: [4, 5, 6] };
      const result = mergeJSONObjects(obj1, obj2);
      expect(result).toEqual({ items: [4, 5, 6] }); // Arrays are replaced, not merged
    });

    it('should handle primitive values', () => {
      const obj1 = { value: 'string' };
      const obj2 = { value: 123 };
      const result = mergeJSONObjects(obj1, obj2);
      expect(result).toEqual({ value: 123 });
    });

    it('should create a new object (not modify originals)', () => {
      const obj1 = { a: 1, b: 2 };
      const obj2 = { c: 3, d: 4 };
      const result = mergeJSONObjects(obj1, obj2);
      
      // Original objects should not be modified
      expect(obj1).toEqual({ a: 1, b: 2 });
      expect(obj2).toEqual({ c: 3, d: 4 });
      
      // Result should be a new object
      expect(result).not.toBe(obj1);
      expect(result).not.toBe(obj2);
    });
  });
});