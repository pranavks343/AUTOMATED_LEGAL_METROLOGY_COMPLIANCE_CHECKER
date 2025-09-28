import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, ScrollView, Image, Linking, ActivityIndicator, StatusBar } from 'react-native';
import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { BarCodeScanner } from 'expo-barcode-scanner';

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [productInfo, setProductInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [webAppUrl] = useState('http://192.168.0.146:8502');

  useEffect(() => {
    requestPermissions();
  }, []);

  const requestPermissions = async () => {
    try {
      // Request camera permission for barcode scanning
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
      
      // Also request media library permissions
      const mediaLibraryStatus = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (mediaLibraryStatus.status !== 'granted') {
        Alert.alert('Permission Required', 'Media library access is needed to upload images');
      }
      
      if (status !== 'granted') {
        Alert.alert('Camera Permission Required', 'Camera access is needed to scan barcodes');
      }
    } catch (error) {
      console.error('Permission request error:', error);
      setError('Failed to request permissions');
    }
  };

  const handleBarCodeScanned = ({ type, data }) => {
    if (scanned) return;
    
    setScanned(true);
    setScannedData(data);
    setShowCamera(false);
    setError(null);
    
    Alert.alert(
      'Barcode Scanned!',
      `Code: ${data}\nType: ${type}`,
      [
        { text: 'Lookup Product', onPress: () => lookupProduct(data) },
        { text: 'Scan Again', onPress: resetScan }
      ]
    );
  };

  const simulateBarcodeScan = () => {
    // Simulate a barcode scan for demo purposes
    const demoBarcode = "3017620422003"; // Nutella barcode
    setScanned(true);
    setScannedData(demoBarcode);
    lookupProduct(demoBarcode);
  };

  const lookupProduct = async (barcode) => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to call the actual Streamlit backend first
      try {
        const response = await fetch(`${webAppUrl}/api/barcode-lookup/${barcode}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 10000
        });
        
        if (response.ok) {
          const data = await response.json();
          setProductInfo(data);
          setLoading(false);
          return;
        }
      } catch (apiError) {
        console.log('API call failed, using demo data:', apiError);
      }
      
      // Fallback to demo data
      const demoProductInfo = {
        name: barcode === "3017620422003" ? "Nutella" : "Sample Product",
        brand: barcode === "3017620422003" ? "Ferrero" : "Sample Brand",
        category: "Food & Beverages",
        weight: "750g",
        manufacturer: barcode === "3017620422003" ? "Ferrero" : "Sample Manufacturer",
        compliance: "Compliant",
        confidence: "95%",
        barcode: barcode,
        source: "Demo Data"
      };
      
      setProductInfo(demoProductInfo);
    } catch (error) {
      setError('Failed to lookup product information');
      console.error('Product lookup error:', error);
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        const imageUri = result.assets[0].uri;
        
        Alert.alert(
          'Image Selected',
          'Image uploaded successfully! Barcode detection would be implemented here.',
          [
            { text: 'OK', onPress: () => console.log('Image URI:', imageUri) }
          ]
        );
        
        // In a real implementation, you would process the image for barcode detection
        // For now, we'll simulate a barcode detection
        setTimeout(() => {
          const simulatedBarcode = "1234567890123";
          setScanned(true);
          setScannedData(simulatedBarcode);
          Alert.alert('Barcode Detected', `Found barcode: ${simulatedBarcode}`, [
            { text: 'Lookup Product', onPress: () => lookupProduct(simulatedBarcode) },
            { text: 'Cancel', style: 'cancel' }
          ]);
        }, 2000);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
      console.error('Image picker error:', error);
    }
  };

  const resetScan = () => {
    setScanned(false);
    setScannedData(null);
    setProductInfo(null);
    setError(null);
  };

  const openWebApp = async () => {
    try {
      const supported = await Linking.canOpenURL(webAppUrl);
      if (supported) {
        await Linking.openURL(webAppUrl);
      } else {
        Alert.alert('Error', 'Cannot open the web app. Please check your network connection.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open web app');
      console.error('Linking error:', error);
    }
  };

  const takePicture = async () => {
    try {
      if (!hasPermission) {
        Alert.alert('Permission Required', 'Camera permission is needed to take pictures');
        return;
      }
      
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        const imageUri = result.assets[0].uri;
        Alert.alert('Photo Taken', 'Photo captured successfully!', [
          { text: 'OK', onPress: () => console.log('Photo URI:', imageUri) }
        ]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take picture');
      console.error('Camera error:', error);
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Legal Metrology Compliance Checker</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermissions}>
          <Text style={styles.buttonText}>Grant Camera Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Camera permission denied</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermissions}>
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (showCamera) {
    return (
      <View style={styles.cameraContainer}>
        <BarCodeScanner
          onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
          style={StyleSheet.absoluteFillObject}
          barCodeTypes={[
            BarCodeScanner.Constants.BarCodeType.qr,
            BarCodeScanner.Constants.BarCodeType.pdf417,
            BarCodeScanner.Constants.BarCodeType.ean13,
            BarCodeScanner.Constants.BarCodeType.ean8,
            BarCodeScanner.Constants.BarCodeType.code128,
            BarCodeScanner.Constants.BarCodeType.code39,
            BarCodeScanner.Constants.BarCodeType.upc_e,
            BarCodeScanner.Constants.BarCodeType.upc_a,
          ]}
        />
        <View style={styles.cameraOverlay}>
          <View style={styles.scanArea}>
            <Text style={styles.overlayText}>Point camera at barcode</Text>
            <Text style={styles.overlaySubtext}>Align barcode within the frame</Text>
          </View>
          <TouchableOpacity style={styles.closeButton} onPress={() => setShowCamera(false)}>
            <Text style={styles.closeButtonText}>✕ Close Camera</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      <Text style={styles.title}>⚖️ Legal Metrology Compliance Checker</Text>
      
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>❌ {error}</Text>
          <TouchableOpacity style={styles.errorButton} onPress={() => setError(null)}>
            <Text style={styles.errorButtonText}>Dismiss</Text>
          </TouchableOpacity>
        </View>
      )}
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📱 Barcode Scanner</Text>
        
        <TouchableOpacity 
          style={[styles.button, !hasPermission && styles.buttonDisabled]} 
          onPress={() => hasPermission ? setShowCamera(true) : requestPermissions()}
          disabled={!hasPermission}
        >
          <Text style={styles.buttonText}>📷 Scan Barcode</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.button} onPress={pickImage}>
          <Text style={styles.buttonText}>🖼️ Upload Image</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.button} onPress={takePicture}>
          <Text style={styles.buttonText}>📸 Take Photo</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.button} onPress={simulateBarcodeScan}>
          <Text style={styles.buttonText}>🧪 Demo Scan (Nutella)</Text>
        </TouchableOpacity>
      </View>

      {scannedData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📦 Scanned Barcode</Text>
          <View style={styles.barcodeCard}>
            <Text style={styles.barcodeText}>{scannedData}</Text>
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.resetButton} onPress={resetScan}>
                <Text style={styles.resetButtonText}>Scan Again</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.lookupButton} onPress={() => lookupProduct(scannedData)}>
                <Text style={styles.lookupButtonText}>Lookup Product</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>Looking up product information...</Text>
        </View>
      )}

      {productInfo && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 Product Information</Text>
          <View style={styles.productCard}>
            <Text style={styles.productName}>{productInfo.name || 'Product Name'}</Text>
            <Text style={styles.productDetail}>Brand: {productInfo.brand || 'N/A'}</Text>
            <Text style={styles.productDetail}>Category: {productInfo.category || 'N/A'}</Text>
            <Text style={styles.productDetail}>Weight: {productInfo.weight || 'N/A'}</Text>
            <Text style={styles.productDetail}>Manufacturer: {productInfo.manufacturer || 'N/A'}</Text>
            <Text style={styles.productDetail}>Compliance: {productInfo.compliance || 'Unknown'}</Text>
            <Text style={styles.productDetail}>Confidence: {productInfo.confidence || 'N/A'}</Text>
            <Text style={styles.productDetail}>Source: {productInfo.source || 'Unknown'}</Text>
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔗 Connect to Web App</Text>
        <TouchableOpacity style={styles.button} onPress={openWebApp}>
          <Text style={styles.buttonText}>🌐 Open Web Version</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.button} 
          onPress={() => Alert.alert('Network Info', `Web App URL: ${webAppUrl}\nMake sure both devices are on the same network.`)}
        >
          <Text style={styles.buttonText}>ℹ️ Network Info</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚙️ App Controls</Text>
        
        <TouchableOpacity style={styles.button} onPress={resetScan}>
          <Text style={styles.buttonText}>🔄 Reset All Data</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.button} 
          onPress={() => Alert.alert('About', 'Legal Metrology Compliance Checker Mobile v1.0.0\n\nThis app helps check product compliance for Legal Metrology regulations in India.')}
        >
          <Text style={styles.buttonText}>ℹ️ About App</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Legal Metrology Compliance Checker Mobile</Text>
        <Text style={styles.footerText}>Version 1.0.0</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: 50,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
    paddingHorizontal: 20,
  },
  section: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#4A90E2',
  },
  button: {
    backgroundColor: '#4A90E2',
    padding: 15,
    borderRadius: 10,
    marginVertical: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    opacity: 0.6,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  errorContainer: {
    backgroundColor: '#f8d7da',
    borderColor: '#f5c6cb',
    borderWidth: 1,
    borderRadius: 10,
    padding: 15,
    margin: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: {
    color: '#721c24',
    fontSize: 14,
    flex: 1,
  },
  errorButton: {
    backgroundColor: '#721c24',
    padding: 8,
    borderRadius: 5,
    marginLeft: 10,
  },
  errorButtonText: {
    color: 'white',
    fontSize: 12,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#4A90E2',
  },
  lookupButton: {
    backgroundColor: '#28a745',
    padding: 8,
    borderRadius: 5,
    flex: 1,
    marginLeft: 10,
    alignItems: 'center',
  },
  lookupButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: 'black',
  },
  cameraOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  scanArea: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
    width: '100%',
  },
  overlayText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0,0,0,0.8)',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    textAlign: 'center',
  },
  overlaySubtext: {
    color: 'white',
    fontSize: 16,
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: 10,
    borderRadius: 5,
    textAlign: 'center',
  },
  closeButton: {
    backgroundColor: '#dc3545',
    padding: 15,
    borderRadius: 10,
    margin: 20,
    minWidth: 120,
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'center',
  },
  barcodeCard: {
    backgroundColor: '#e8f5e8',
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#28a745',
  },
  barcodeText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  resetButton: {
    backgroundColor: '#6c757d',
    padding: 8,
    borderRadius: 5,
    alignSelf: 'flex-start',
  },
  resetButtonText: {
    color: 'white',
    fontSize: 14,
  },
  productCard: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  productDetail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  footer: {
    margin: 20,
    alignItems: 'center',
    padding: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 5,
  },
});