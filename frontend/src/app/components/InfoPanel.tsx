"use client";

import { useState } from "react";
import ForecastChart from "./ForecastChart";

// TypeScript interface for Station data
interface Station {
	id: number;
	name: string;
	coordinates: {
		latitude: number;
		longitude: number;
	};
	sensors: Array<{
		parameter: {
			id: number;
			name: string;
			units: string;
			displayName: string;
		};
	}>;
	datetimeLast: {
		utc: string;
		local: string;
	};
	distance: number;
}

// Interface for component props
interface InfoPanelProps {
	stations: Station[];
	lat: number;
	lon: number;
	children?: React.ReactNode;
}

export default function InfoPanel({
	stations,
	lat,
	lon,
	children,
}: InfoPanelProps) {
	// State for Report Modal
	const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);

	// Function to find the highest PM2.5 value from all stations
	const getHighestPM25 = (): number => {
		if (!stations || stations.length === 0) return 0;

		let highestValue = 0;

		stations.forEach((station) => {
			if (station.sensors && station.sensors.length > 0) {
				station.sensors.forEach((sensor) => {
					// Check if this sensor measures PM2.5
					if (
						sensor.parameter.name.toLowerCase().includes("pm25") ||
						sensor.parameter.name.toLowerCase().includes("pm2.5")
					) {
						// Note: We would need actual measurement values from a different endpoint
						// For now, we'll use a placeholder value
						// In a real scenario, you'd fetch latest measurements
						highestValue = Math.max(highestValue, 0);
					}
				});
			}
		});

		return highestValue;
	};

	// Function to get unique pollutants being monitored
	const getMonitoredPollutants = (): string[] => {
		if (!stations || stations.length === 0) return [];

		const pollutantSet = new Set<string>();

		stations.forEach((station) => {
			if (station.sensors && station.sensors.length > 0) {
				station.sensors.forEach((sensor) => {
					pollutantSet.add(sensor.parameter.displayName);
				});
			}
		});

		return Array.from(pollutantSet);
	};

	// Function to get plain-language air quality summary based on PM2.5 value
	const getAirQualitySummary = (pm25Value: number): string => {
		if (pm25Value === 0) return "No PM2.5 data available";
		if (pm25Value <= 12) return "Good";
		if (pm25Value <= 35.4) return "Moderate";
		if (pm25Value <= 55.4) return "Unhealthy for Sensitive Groups";
		if (pm25Value <= 150.4) return "Unhealthy";
		if (pm25Value <= 250.4) return "Very Unhealthy";
		return "Hazardous";
	};

	// Function to get color based on air quality level
	const getAQIColor = (pm25Value: number): string => {
		if (pm25Value === 0) return "#9CA3AF";
		if (pm25Value <= 12) return "#10B981"; // Green
		if (pm25Value <= 35.4) return "#FBBF24"; // Yellow
		if (pm25Value <= 55.4) return "#F97316"; // Orange
		if (pm25Value <= 150.4) return "#EF4444"; // Red
		if (pm25Value <= 250.4) return "#A855F7"; // Purple
		return "#991B1B"; // Dark Red
	};

	const highestPM25 = getHighestPM25();
	const aqiSummary = getAirQualitySummary(highestPM25);
	const aqiColor = getAQIColor(highestPM25);
	const monitoredPollutants = getMonitoredPollutants();

	// Count active stations (data from last 30 days)
	const activeStations = stations.filter((station) => {
		const lastUpdate = new Date(station.datetimeLast.utc);
		const thirtyDaysAgo = new Date();
		thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
		return lastUpdate > thirtyDaysAgo;
	});

	return (
		<div
			style={{
				position: "absolute",
				top: "20px",
				right: "20px",
				width: "400px",
				height: "calc(100vh - 40px)",
				backgroundColor: "rgba(31, 41, 55, 0.2)",
					backdropFilter: "blur(4px)",
					borderRadius: "12px",
					boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
					border: "1px solid rgba(255, 255, 255, 0.2)",
					zIndex: 1000,
					display: "flex",
					flexDirection: "column",
					overflow: "hidden",
				}}>
			{/* Fixed Header */}
			<div
				style={{
					padding: "24px",
					borderBottom: "1px solid #374151",
					flexShrink: 0,
				}}>
				<h2
					style={{
						margin: "0 0 8px 0",
						fontSize: "24px",
						fontWeight: "bold",
						color: "#F9FAFB",
					}}>
					NYC Area Air Quality
				</h2>
				<p
					style={{
						margin: 0,
						fontSize: "14px",
						color: "#9CA3AF",
					}}>
					Community AirShield
				</p>
			</div>

			{/* Scrollable Content */}
			<div
				style={{
					flex: 1,
					overflowY: "auto",
					padding: "24px",
				}}>
				{/* At-a-Glance Section */}
				<div
					style={{
						padding: "20px",
						backgroundColor: "#374151",
						borderRadius: "12px",
						marginBottom: "24px",
						borderLeft: `4px solid #10B981`,
					}}>
					<h3
						style={{
							margin: "0 0 16px 0",
							fontSize: "18px",
							fontWeight: "600",
							color: "#F9FAFB",
						}}>
						At-a-Glance
					</h3>

					<div style={{ marginBottom: "16px" }}>
						<p
							style={{
								margin: "0 0 8px 0",
								fontSize: "12px",
								color: "#9CA3AF",
								textTransform: "uppercase",
								fontWeight: "600",
								letterSpacing: "0.5px",
							}}>
							Network Status
						</p>
						<p
							style={{
								margin: 0,
								fontSize: "32px",
								fontWeight: "bold",
								color: "#10B981",
							}}>
							✅ Active
						</p>
					</div>

					<div style={{ marginBottom: "16px" }}>
						<p
							style={{
								margin: "0 0 8px 0",
								fontSize: "12px",
								color: "#9CA3AF",
								textTransform: "uppercase",
								fontWeight: "600",
								letterSpacing: "0.5px",
							}}>
							Monitoring Stations Online
						</p>
						<p
							style={{
								margin: 0,
								fontSize: "24px",
								fontWeight: "600",
								color: "#F9FAFB",
							}}>
							{activeStations.length}{" "}
							<span
								style={{
									fontSize: "16px",
									color: "#9CA3AF",
								}}>
								of {stations.length}
							</span>
						</p>
					</div>

					{monitoredPollutants.length > 0 && (
						<div>
							<p
								style={{
									margin: "0 0 8px 0",
									fontSize: "12px",
									color: "#9CA3AF",
									textTransform: "uppercase",
									fontWeight: "600",
									letterSpacing: "0.5px",
								}}>
								Measuring
							</p>
							<p
								style={{
									margin: 0,
									fontSize: "14px",
									fontWeight: "500",
									color: "#F9FAFB",
									lineHeight: "1.6",
								}}>
								{monitoredPollutants.join(", ")}
							</p>
						</div>
					)}
				</div>

				{/* Station Summary */}
				<div
					style={{
						padding: "20px",
						backgroundColor: "#374151",
						borderRadius: "12px",
						marginBottom: "24px",
					}}>
					<h3
						style={{
							margin: "0 0 16px 0",
							fontSize: "18px",
							fontWeight: "600",
							color: "#F9FAFB",
						}}>
						Monitoring Stations
					</h3>

					<div
						style={{
							display: "flex",
							justifyContent: "space-between",
							marginBottom: "12px",
						}}>
						<span style={{ fontSize: "14px", color: "#9CA3AF" }}>
							Total Stations:
						</span>
						<span
							style={{
								fontSize: "14px",
								fontWeight: "600",
								color: "#F9FAFB",
							}}>
							{stations.length}
						</span>
					</div>

					<div
						style={{
							display: "flex",
							justifyContent: "space-between",
						}}>
						<span style={{ fontSize: "14px", color: "#9CA3AF" }}>
							Active Stations:
						</span>
						<span
							style={{
								fontSize: "14px",
								fontWeight: "600",
								color: "#10B981",
							}}>
							{activeStations.length}
						</span>
					</div>
				</div>

				{/* Station List */}
				<div
					style={{
						padding: "20px",
						backgroundColor: "#374151",
						borderRadius: "12px",
						marginBottom: "24px",
					}}>
					<h3
						style={{
							margin: "0 0 16px 0",
							fontSize: "18px",
							fontWeight: "600",
							color: "#F9FAFB",
						}}>
						Nearby Stations
					</h3>

					{stations.map((station) => {
						const lastUpdate = new Date(station.datetimeLast.utc);
						const thirtyDaysAgo = new Date();
						thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
						const isActive = lastUpdate > thirtyDaysAgo;

						return (
							<div
								key={station.id}
								style={{
									padding: "14px",
									marginBottom: "10px",
									backgroundColor: "#1F2937",
									borderRadius: "8px",
									borderLeft: `3px solid ${
										isActive ? "#10B981" : "#EF4444"
									}`,
									cursor: "pointer",
									transition: "background-color 0.2s",
								}}
								onMouseEnter={(e) => {
									e.currentTarget.style.backgroundColor = "#4B5563";
								}}
								onMouseLeave={(e) => {
									e.currentTarget.style.backgroundColor = "#1F2937";
								}}>
								<div
									style={{
										display: "flex",
										justifyContent: "space-between",
										alignItems: "start",
									}}>
									<div style={{ flex: 1 }}>
										<p
											style={{
												margin: "0 0 6px 0",
												fontSize: "14px",
												fontWeight: "600",
												color: "#F9FAFB",
											}}>
											{station.name}
										</p>
										<p
											style={{
												margin: "0 0 4px 0",
												fontSize: "12px",
												color: "#9CA3AF",
											}}>
											📍{" "}
											{(station.distance / 1000).toFixed(
												2
											)}{" "}
											km away
										</p>
										{station.sensors &&
											station.sensors.length > 0 && (
												<p
													style={{
														margin: 0,
														fontSize: "12px",
														color: "#9CA3AF",
													}}>
													Measuring:{" "}
													{
														station.sensors[0]
															.parameter
															.displayName
													}
												</p>
											)}
									</div>
									<div
										style={{
											fontSize: "10px",
											fontWeight: "600",
											color: isActive
												? "#10B981"
												: "#EF4444",
											backgroundColor: isActive
												? "#D1FAE5"
												: "#FEE2E2",
											padding: "4px 8px",
											borderRadius: "4px",
										}}>
										{isActive ? "ACTIVE" : "INACTIVE"}
									</div>
								</div>
							</div>
						);
					})}
				</div>
			</div>

		{/* Fixed Footer Section - Toggle Button */}
		<div
			style={{
				flexShrink: 0,
				borderTop: "2px solid #374151",
				backgroundColor: "#1F2937",
			}}>
			{/* Footer Info */}
			<div
				style={{
					padding: "16px 24px",
				}}>
				<p
					style={{
						margin: 0,
						fontSize: "11px",
						color: "#6B7280",
						textAlign: "center",
					}}>
					Data provided by OpenAQ
				</p>
			</div>

			{/* Render children (e.g., toggle button) */}
			<div style={{ padding: "0 24px 24px 24px" }}>{children}</div>
		</div>			{/* Report Modal */}
			{isReportModalOpen && (
				<div
					style={{
						position: "fixed",
						inset: 0,
						backgroundColor: "rgba(0, 0, 0, 0.7)",
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						zIndex: 9999,
					}}
					onClick={() => setIsReportModalOpen(false)}>
					<div
						style={{
							backgroundColor: "rgba(31, 41, 55, 0.9)",
							backdropFilter: "blur(16px)",
							borderRadius: "16px",
							boxShadow: "0 20px 50px rgba(0, 0, 0, 0.5)",
							padding: "32px",
							border: "1px solid rgba(255, 255, 255, 0.2)",
							width: "90%",
							maxWidth: "800px",
							maxHeight: "90vh",
							overflowY: "auto",
						}}
						onClick={(e) => e.stopPropagation()}>
						{/* Modal Header */}
						<div
							style={{
								display: "flex",
								justifyContent: "space-between",
								alignItems: "center",
								marginBottom: "24px",
								paddingBottom: "16px",
								borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
							}}>
							<h2
								style={{
									margin: 0,
									fontSize: "28px",
									fontWeight: "bold",
									color: "#F9FAFB",
								}}>
								📋 Current Air Quality Report
							</h2>
							<button
								onClick={() => setIsReportModalOpen(false)}
								style={{
									background: "rgba(239, 68, 68, 0.2)",
									border: "1px solid rgba(239, 68, 68, 0.5)",
									borderRadius: "8px",
									color: "#FEE2E2",
									cursor: "pointer",
									fontSize: "16px",
									fontWeight: "600",
									padding: "8px 16px",
									transition: "all 0.2s",
								}}
								onMouseEnter={(e) => {
									e.currentTarget.style.backgroundColor = "rgba(239, 68, 68, 0.4)";
								}}
								onMouseLeave={(e) => {
									e.currentTarget.style.backgroundColor = "rgba(239, 68, 68, 0.2)";
								}}>
								✕ Close
							</button>
						</div>

						{/* Report Timestamp */}
						<div
							style={{
								marginBottom: "24px",
								padding: "12px",
								backgroundColor: "rgba(55, 65, 81, 0.5)",
								borderRadius: "8px",
								borderLeft: "4px solid #3B82F6",
							}}>
							<p
								style={{
									margin: 0,
									fontSize: "14px",
									color: "#9CA3AF",
								}}>
								<span style={{ fontWeight: "600", color: "#F9FAFB" }}>Report Generated:</span>{" "}
								{new Date().toLocaleString("en-US", {
									weekday: "long",
									year: "numeric",
									month: "long",
									day: "numeric",
									hour: "2-digit",
									minute: "2-digit",
								})}
							</p>
						</div>

						{/* Summary Section */}
						<div
							style={{
								marginBottom: "24px",
								padding: "24px",
								backgroundColor: "rgba(55, 65, 81, 0.5)",
								borderRadius: "12px",
								borderLeft: `6px solid ${aqiColor}`,
							}}>
							<h3
								style={{
									margin: "0 0 16px 0",
									fontSize: "20px",
									fontWeight: "600",
									color: "#F9FAFB",
								}}>
								🌍 At-a-Glance Summary
							</h3>
							<div
								style={{
									display: "grid",
									gridTemplateColumns: "1fr 1fr",
									gap: "20px",
								}}>
								<div>
									<p
										style={{
											margin: "0 0 8px 0",
											fontSize: "12px",
											color: "#9CA3AF",
											textTransform: "uppercase",
											fontWeight: "600",
											letterSpacing: "1px",
										}}>
										Current Status
									</p>
									<p
										style={{
											margin: 0,
											fontSize: "36px",
											fontWeight: "bold",
											color: aqiColor,
										}}>
										{aqiSummary}
									</p>
								</div>
								{highestPM25 > 0 && (
									<div>
										<p
											style={{
												margin: "0 0 8px 0",
												fontSize: "12px",
												color: "#9CA3AF",
												textTransform: "uppercase",
												fontWeight: "600",
												letterSpacing: "1px",
											}}>
											Highest PM2.5 Reading
										</p>
										<p
											style={{
												margin: 0,
												fontSize: "36px",
												fontWeight: "bold",
												color: "#F9FAFB",
											}}>
											{highestPM25.toFixed(1)}{" "}
											<span
												style={{
													fontSize: "18px",
													color: "#9CA3AF",
												}}>
												µg/m³
											</span>
										</p>
									</div>
								)}
							</div>
						</div>

						{/* Monitoring Stations Section */}
						<div
							style={{
								marginBottom: "24px",
								padding: "24px",
								backgroundColor: "rgba(55, 65, 81, 0.5)",
								borderRadius: "12px",
							}}>
							<h3
								style={{
									margin: "0 0 16px 0",
									fontSize: "20px",
									fontWeight: "600",
									color: "#F9FAFB",
								}}>
								📡 Monitoring Network Status
							</h3>
							<div
								style={{
									display: "grid",
									gridTemplateColumns: "1fr 1fr 1fr",
									gap: "16px",
								}}>
								<div
									style={{
										padding: "16px",
										backgroundColor: "rgba(31, 41, 55, 0.6)",
										borderRadius: "8px",
										textAlign: "center",
									}}>
									<p
										style={{
											margin: "0 0 8px 0",
											fontSize: "12px",
											color: "#9CA3AF",
											textTransform: "uppercase",
										}}>
										Total Stations
									</p>
									<p
										style={{
											margin: 0,
											fontSize: "32px",
											fontWeight: "bold",
											color: "#F9FAFB",
										}}>
										{stations.length}
									</p>
								</div>
								<div
									style={{
										padding: "16px",
										backgroundColor: "rgba(31, 41, 55, 0.6)",
										borderRadius: "8px",
										textAlign: "center",
									}}>
									<p
										style={{
											margin: "0 0 8px 0",
											fontSize: "12px",
											color: "#9CA3AF",
											textTransform: "uppercase",
										}}>
										Active Stations
									</p>
									<p
										style={{
											margin: 0,
											fontSize: "32px",
											fontWeight: "bold",
											color: "#10B981",
										}}>
										{activeStations.length}
									</p>
								</div>
								<div
									style={{
										padding: "16px",
										backgroundColor: "rgba(31, 41, 55, 0.6)",
										borderRadius: "8px",
										textAlign: "center",
									}}>
									<p
										style={{
											margin: "0 0 8px 0",
											fontSize: "12px",
											color: "#9CA3AF",
											textTransform: "uppercase",
										}}>
										Network Coverage
									</p>
									<p
										style={{
											margin: 0,
											fontSize: "32px",
											fontWeight: "bold",
											color: "#3B82F6",
										}}>
										{((activeStations.length / stations.length) * 100).toFixed(0)}%
									</p>
								</div>
							</div>
							<p
								style={{
									margin: "16px 0 0 0",
									fontSize: "14px",
									color: "#9CA3AF",
									textAlign: "center",
								}}>
								{activeStations.length} out of {stations.length} monitoring stations are currently active
								(updated within the last 30 days)
							</p>
						</div>

						{/* Forecast Section */}
						<div
							style={{
								marginBottom: "24px",
								padding: "24px",
								backgroundColor: "rgba(55, 65, 81, 0.5)",
								borderRadius: "12px",
							}}>
							<h3
								style={{
									margin: "0 0 16px 0",
									fontSize: "20px",
									fontWeight: "600",
									color: "#F9FAFB",
								}}>
								📈 24-Hour Forecast
							</h3>
							<div
								style={{
									backgroundColor: "rgba(31, 41, 55, 0.6)",
									borderRadius: "8px",
									padding: "16px",
								}}>
								<ForecastChart lat={lat} lon={lon} />
							</div>
						</div>

						{/* Footer Note */}
						<div
							style={{
								padding: "16px",
								backgroundColor: "rgba(55, 65, 81, 0.5)",
								borderRadius: "8px",
								textAlign: "center",
							}}>
							<p
								style={{
									margin: 0,
									fontSize: "12px",
									color: "#9CA3AF",
								}}>
								💡 This report provides a snapshot of current air quality conditions in the NYC area.
								<br />
								Data is sourced from OpenAQ monitoring network.
							</p>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
