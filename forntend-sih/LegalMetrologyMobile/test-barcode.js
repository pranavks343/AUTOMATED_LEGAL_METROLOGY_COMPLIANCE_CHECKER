// Test file to verify barcode scanning functionality
import { BarCodeScanner } from 'expo-barcode-scanner';

console.log('Testing barcode scanner...');

// Test if BarCodeScanner is properly imported
console.log('BarCodeScanner imported:', !!BarCodeScanner);
console.log('BarCodeScanner.Constants:', BarCodeScanner.Constants);
console.log('BarCodeScanner.Constants.BarCodeType:', BarCodeScanner.Constants.BarCodeType);

// Test supported barcode types
const supportedTypes = [
  BarCodeScanner.Constants.BarCodeType.qr,
  BarCodeScanner.Constants.BarCodeType.pdf417,
  BarCodeScanner.Constants.BarCodeType.ean13,
  BarCodeScanner.Constants.BarCodeType.ean8,
  BarCodeScanner.Constants.BarCodeType.code128,
  BarCodeScanner.Constants.BarCodeType.code39,
  BarCodeScanner.Constants.BarCodeType.upc_e,
  BarCodeScanner.Constants.BarCodeType.upc_a,
];

console.log('Supported barcode types:', supportedTypes);

export default function testBarcodeScanner() {
  return {
    scannerAvailable: !!BarCodeScanner,
    supportedTypes: supportedTypes,
    constantsAvailable: !!BarCodeScanner.Constants
  };
}
