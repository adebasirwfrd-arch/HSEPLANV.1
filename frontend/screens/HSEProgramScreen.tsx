import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    Modal,
    TextInput,
    StyleSheet,
    ActivityIndicator,
    Alert,
    Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import { hseApiService, HSEProgram, ProgramUpdate } from '../services/api';

const HSEProgramScreen = () => {
    const [programs, setPrograms] = useState<HSEProgram[]>([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [isModalVisible, setModalVisible] = useState(false);
    const [selectedProgram, setSelectedProgram] = useState<HSEProgram | null>(null);

    // Form Fields
    const [actualDate, setActualDate] = useState(new Date());
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [status, setStatus] = useState<'Open' | 'Closed'>('Open');
    const [wptsNumber, setWptsNumber] = useState('');
    const [evidenceUrl, setEvidenceUrl] = useState('');
    const [formError, setFormError] = useState('');

    useEffect(() => {
        fetchPrograms();
    }, []);

    const fetchPrograms = async () => {
        try {
            setLoading(true);
            const data = await hseApiService.getPrograms();
            setPrograms(data);
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Failed to load programs');
        } finally {
            setLoading(false);
        }
    };

    const openUpdateModal = (program: HSEProgram) => {
        setSelectedProgram(program);
        setActualDate(new Date());
        setStatus('Open');
        setWptsNumber('');
        setEvidenceUrl('');
        setFormError('');
        setModalVisible(true);
    };

    const closeModal = () => {
        setModalVisible(false);
        setSelectedProgram(null);
        setFormError('');
    };

    const validateForm = (): boolean => {
        if (!wptsNumber.trim()) {
            setFormError('WPTS Number is required');
            return false;
        }
        setFormError('');
        return true;
    };

    const handleSubmit = async () => {
        if (!selectedProgram) return;
        if (!validateForm()) return;

        setSubmitting(true);
        try {
            const updateData: ProgramUpdate = {
                actual_date: actualDate.toISOString(),
                status,
                wpts_number: wptsNumber.trim(),
                evidence_link: evidenceUrl.trim() || undefined,
            };

            await hseApiService.updateProgram(selectedProgram.id, updateData);
            closeModal();
            Alert.alert('Success', 'Program updated successfully');
            fetchPrograms(); // Refresh list
        } catch (error) {
            console.error(error);
            Alert.alert('Error', error instanceof Error ? error.message : 'Update failed');
        } finally {
            setSubmitting(false);
        }
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    const getStatusColor = (programStatus: string): string => {
        switch (programStatus.toLowerCase()) {
            case 'closed':
                return '#34C759';
            case 'open':
                return '#FF9500';
            default:
                return '#8E8E93';
        }
    };

    const renderItem = ({ item }: { item: HSEProgram }) => (
        <View style={styles.card}>
            <View style={styles.cardHeader}>
                <Text style={styles.title}>{item.title}</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                    <Text style={styles.statusText}>{item.status}</Text>
                </View>
            </View>
            <View style={styles.cardDetails}>
                <Text style={styles.detailText}>
                    📅 Planned: {formatDate(item.planned_date)}
                </Text>
                {item.actual_date && (
                    <Text style={styles.detailText}>
                        ✅ Actual: {formatDate(item.actual_date)}
                    </Text>
                )}
                {item.wpts_number && (
                    <Text style={styles.detailText}>
                        🔖 WPTS: {item.wpts_number}
                    </Text>
                )}
            </View>
            <TouchableOpacity
                style={styles.updateButton}
                onPress={() => openUpdateModal(item)}
            >
                <Text style={styles.buttonText}>Update Status</Text>
            </TouchableOpacity>
        </View>
    );

    if (loading) {
        return (
            <View style={styles.loaderContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loaderText}>Loading programs...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.header}>HSE Programs</Text>
            <Text style={styles.subHeader}>{programs.length} program(s) found</Text>

            <FlatList
                data={programs}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderItem}
                contentContainerStyle={styles.listContainer}
                showsVerticalScrollIndicator={false}
                refreshing={loading}
                onRefresh={fetchPrograms}
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No programs found</Text>
                    </View>
                }
            />

            <Modal visible={isModalVisible} animationType="slide" transparent={true}>
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <Text style={styles.modalHeader}>Update Program Status</Text>
                        {selectedProgram && (
                            <Text style={styles.modalSubtitle}>{selectedProgram.title}</Text>
                        )}

                        {formError ? (
                            <View style={styles.errorContainer}>
                                <Text style={styles.errorText}>{formError}</Text>
                            </View>
                        ) : null}

                        <Text style={styles.label}>Actual Date *</Text>
                        <TouchableOpacity
                            onPress={() => setShowDatePicker(true)}
                            style={styles.dateInput}
                        >
                            <Text>{actualDate.toLocaleDateString()}</Text>
                        </TouchableOpacity>
                        {showDatePicker && (
                            <DateTimePicker
                                value={actualDate}
                                mode="date"
                                display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                                onChange={(event, date) => {
                                    setShowDatePicker(Platform.OS === 'ios');
                                    if (date) setActualDate(date);
                                }}
                            />
                        )}

                        <Text style={styles.label}>Status *</Text>
                        <View style={styles.pickerContainer}>
                            <Picker
                                selectedValue={status}
                                onValueChange={(itemValue) => setStatus(itemValue)}
                                style={styles.picker}
                            >
                                <Picker.Item label="Open" value="Open" />
                                <Picker.Item label="Closed" value="Closed" />
                            </Picker>
                        </View>

                        <Text style={styles.label}>WPTS Number * (Required)</Text>
                        <TextInput
                            style={[styles.input, !wptsNumber && formError ? styles.inputError : null]}
                            value={wptsNumber}
                            onChangeText={(text) => {
                                setWptsNumber(text);
                                if (formError) setFormError('');
                            }}
                            placeholder="Enter WPTS Number"
                            placeholderTextColor="#999"
                        />

                        <Text style={styles.label}>Evidence URL (Optional)</Text>
                        <TextInput
                            style={styles.input}
                            value={evidenceUrl}
                            onChangeText={setEvidenceUrl}
                            placeholder="Enter Evidence URL"
                            placeholderTextColor="#999"
                            keyboardType="url"
                            autoCapitalize="none"
                        />

                        <View style={styles.modalButtons}>
                            <TouchableOpacity
                                style={[styles.modalButton, styles.cancelButton]}
                                onPress={closeModal}
                                disabled={submitting}
                            >
                                <Text style={styles.cancelButtonText}>Cancel</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                style={[styles.modalButton, styles.submitButton, submitting && styles.disabledButton]}
                                onPress={handleSubmit}
                                disabled={submitting}
                            >
                                {submitting ? (
                                    <ActivityIndicator size="small" color="#fff" />
                                ) : (
                                    <Text style={styles.submitButtonText}>Submit</Text>
                                )}
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    header: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#1a1a1a',
    },
    subHeader: {
        fontSize: 14,
        color: '#666',
        marginBottom: 20,
    },
    listContainer: {
        paddingBottom: 20,
    },
    loaderContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
    },
    loaderText: {
        marginTop: 10,
        color: '#666',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingTop: 50,
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
    },
    card: {
        backgroundColor: 'white',
        padding: 16,
        borderRadius: 12,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    title: {
        fontSize: 18,
        fontWeight: '600',
        color: '#1a1a1a',
        flex: 1,
    },
    statusBadge: {
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
    },
    statusText: {
        color: 'white',
        fontSize: 12,
        fontWeight: '600',
    },
    cardDetails: {
        marginBottom: 12,
    },
    detailText: {
        fontSize: 14,
        color: '#666',
        marginBottom: 4,
    },
    updateButton: {
        backgroundColor: '#007AFF',
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
    },
    buttonText: {
        color: 'white',
        fontWeight: '600',
        fontSize: 16,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        padding: 20,
    },
    modalContent: {
        backgroundColor: 'white',
        padding: 24,
        borderRadius: 16,
        maxHeight: '80%',
    },
    modalHeader: {
        fontSize: 22,
        fontWeight: 'bold',
        marginBottom: 4,
        color: '#1a1a1a',
    },
    modalSubtitle: {
        fontSize: 14,
        color: '#666',
        marginBottom: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        marginTop: 12,
        marginBottom: 6,
        color: '#333',
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        padding: 12,
        borderRadius: 8,
        fontSize: 16,
        backgroundColor: '#fafafa',
    },
    inputError: {
        borderColor: '#FF3B30',
    },
    dateInput: {
        borderWidth: 1,
        borderColor: '#ddd',
        padding: 12,
        borderRadius: 8,
        backgroundColor: '#fafafa',
    },
    pickerContainer: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        backgroundColor: '#fafafa',
        overflow: 'hidden',
    },
    picker: {
        height: 50,
    },
    errorContainer: {
        backgroundColor: '#FFE5E5',
        padding: 10,
        borderRadius: 8,
        marginBottom: 10,
    },
    errorText: {
        color: '#FF3B30',
        fontSize: 14,
    },
    modalButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 24,
        gap: 12,
    },
    modalButton: {
        flex: 1,
        padding: 14,
        borderRadius: 8,
        alignItems: 'center',
    },
    cancelButton: {
        backgroundColor: '#f0f0f0',
    },
    cancelButtonText: {
        color: '#666',
        fontWeight: '600',
        fontSize: 16,
    },
    submitButton: {
        backgroundColor: '#007AFF',
    },
    submitButtonText: {
        color: 'white',
        fontWeight: '600',
        fontSize: 16,
    },
    disabledButton: {
        opacity: 0.6,
    },
});

export default HSEProgramScreen;
