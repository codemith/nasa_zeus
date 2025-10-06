"use client";

import { useEffect, useState } from "react";
import {
	MapContainer,
	TileLayer,
	Marker,
	Popup,
	Pane,
	LayersControl,
	CircleMarker,
} from "react-leaflet";
import { HeatmapLayer } from "react-leaflet-heatmap-layer-v3";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

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

// Function to create custom icon based on pollutant type
const createCustomIcon = (parameterName: string, isActive: boolean) => {
	// Determine color based on parameter type
	let color = "#6B7280"; // Default gray
	let symbol = "☁️";

	if (
		parameterName.toLowerCase().includes("o3") ||
		parameterName.toLowerCase().includes("ozone")
	) {
		color = isActive ? "#3B82F6" : "#93C5FD"; // Blue for ozone
		symbol = "○₃";
	} else if (parameterName.toLowerCase().includes("pm")) {
		color = isActive ? "#8B5CF6" : "#C4B5FD"; // Purple for particulate matter
		symbol = "◉";
	} else if (
		parameterName.toLowerCase().includes("no2") ||
		parameterName.toLowerCase().includes("nitrogen")
	) {
		color = isActive ? "#EF4444" : "#FCA5A5"; // Red for nitrogen dioxide
		symbol = "◈";
	} else if (
		parameterName.toLowerCase().includes("temperature") ||
		parameterName.toLowerCase().includes("humidity")
	) {
		color = isActive ? "#10B981" : "#6EE7B7"; // Green for environmental
		symbol = "◐";
	}

	const iconHtml = `
    <div style="
      position: relative;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="
        width: 32px;
        height: 32px;
        background: ${color};
        border: 3px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-size: 16px;
        font-weight: bold;
        color: white;
        ${isActive ? "animation: pulse 2s infinite;" : ""}
      ">
        ${symbol}
      </div>
      <div style="
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 8px solid ${color};
        filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2));
      "></div>
    </div>
    <style>
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
    </style>
  `;

	return L.divIcon({
		html: iconHtml,
		className: "custom-marker",
		iconSize: [40, 40],
		iconAnchor: [20, 32],
		popupAnchor: [0, -32],
	});
};

interface TempoData {
	value: string;
	location: {
		x: number;
		y: number;
	};
}

// TypeScript interface for Surface Pressure data
interface SurfacePressureData {
	current: {
		timestamp: string;
		pressure_pa: number;
		pressure_hpa: number;
		pressure_inhg: number;
		source: string;
		station: string;
		quality: string;
	};
	location: {
		lat: number;
		lon: number;
	};
	summary: {
		avg_hpa: number;
		min_hpa: number;
		max_hpa: number;
	};
}

// TypeScript interface for NOAA Wind data
interface NOAAWindData {
	meta: {
		source: string;
		location: {
			lat: number;
			lon: number;
			grid_id: string;
			grid_x: number;
			grid_y: number;
		};
		forecast_periods: number;
		update_time: string;
	};
	current: {
		forecast_hour: number;
		start_time: string;
		temperature: number;
		temperature_unit: string;
		wind_speed_mph: number;
		wind_speed_ms: number;
		wind_direction: string;
		wind_direction_degrees: number;
		u_component: number;
		v_component: number;
		humidity: number;
		detailed_forecast: string;
	};
	forecast: Array<{
		forecast_hour: number;
		start_time: string;
		temperature: number;
		wind_speed_mph: number;
		wind_speed_ms: number;
		wind_direction: string;
		wind_direction_degrees: number;
		u_component: number;
		v_component: number;
		humidity: number;
	}>;
}

// Interface for processed wind vectors on map
interface WindVector {
	lat: number;
	lon: number;
	u: number;
	v: number;
	speed: number;
	direction: number;
	source: "noaa" | "demo";
}

export default function Map() {
	// New York City coordinates
	const position: [number, number] = [40.7128, -74.006];
	const zoom = 10; // Zoomed out to see larger area
	const [stations, setStations] = useState<Station[]>([]);
	const [tempoData, setTempoData] = useState<TempoData | null>(null);
	const [surfacePressureData, setSurfacePressureData] = useState<SurfacePressureData | null>(null);
	const [showHeatmap, setShowHeatmap] = useState<boolean>(false);
	const [heatmapData, setHeatmapData] = useState<
		Array<[number, number, number]>
	>([]);
	const [showWindLayer, setShowWindLayer] = useState<boolean>(true);
	const [windData, setWindData] = useState<NOAAWindData | null>(null);
	const [windVectors, setWindVectors] = useState<WindVector[]>([]);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const apiBaseUrl =
					process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

				// Fetch TEMPO NO2 data
				const tempoResponse = await fetch(
					`${apiBaseUrl}/api/tempo_json`
				);
				if (!tempoResponse.ok) {
					throw new Error(
						`HTTP error! status: ${tempoResponse.status}`
					);
				}
				const tempoData = await tempoResponse.json();
				console.log("TEMPO NO2 data:", tempoData);
				setTempoData(tempoData);

				// Fetch surface pressure data for NYC
				try {
					console.log("🌡️ Fetching surface pressure data for NYC...");
					const pressureResponse = await fetch(
						`${apiBaseUrl}/api/surface-pressure?lat=40.7128&lon=-74.0060&hours_back=1&hours_forward=0&include_forecast=false`
					);
					if (pressureResponse.ok) {
						const pressureResult = await pressureResponse.json();
						console.log("✅ Surface pressure data received:", pressureResult);
						
						// Extract the latest observation for display
						if (pressureResult.success && pressureResult.data) {
							const data = pressureResult.data;
							const latestObs = data.observation_data && data.observation_data.length > 0 
								? data.observation_data[data.observation_data.length - 1]
								: null;
							
							if (latestObs) {
								const pressureDisplayData: SurfacePressureData = {
									current: {
										timestamp: latestObs.timestamp,
										pressure_pa: latestObs.pressure_pa,
										pressure_hpa: latestObs.pressure_hpa,
										pressure_inhg: latestObs.pressure_inhg,
										source: latestObs.source,
										station: latestObs.station,
										quality: latestObs.quality
									},
									location: {
										lat: data.location.lat,
										lon: data.location.lon
									},
									summary: data.summary?.pressure_stats || {
										avg_hpa: latestObs.pressure_hpa,
										min_hpa: latestObs.pressure_hpa,
										max_hpa: latestObs.pressure_hpa
									}
								};
								setSurfacePressureData(pressureDisplayData);
							}
						}
					} else {
						console.warn("⚠️ Surface pressure data failed:", pressureResponse.status);
					}
				} catch (pressureError) {
					console.warn("⚠️ Surface pressure data failed:", pressureError);
				}

				// Fetch stations data with 100km radius (expands search area)
				const stationsResponse = await fetch(
					`${apiBaseUrl}/api/openaq-latest?lat=40.7128&lon=-74.0060&radius=100000`
				);
				if (!stationsResponse.ok) {
					throw new Error(
						`HTTP error! status: ${stationsResponse.status}`
					);
				}
				const stationsData = await stationsResponse.json();
				if (
					stationsData.results &&
					Array.isArray(stationsData.results)
				) {
					setStations(stationsData.results);
				}

				// Fetch TEMPO grid data for heat map (NYC bounding box)
				const north = 40.9;
				const south = 40.5;
				const east = -73.7;
				const west = -74.3;
				const gridResponse = await fetch(
					`${apiBaseUrl}/api/tempo-grid?north=${north}&south=${south}&east=${east}&west=${west}`
				);
				if (gridResponse.ok) {
					const gridData = await gridResponse.json();
					console.log("Heat map grid data:", gridData);
					setHeatmapData(gridData);
				}

				// Fetch NOAA GFS wind data for NYC
				console.log("🌪️ Fetching NOAA wind data...");
				const windResponse = await fetch(
					`${apiBaseUrl}/api/noaa-wind-data?lat=40.7128&lon=-74.0060`
				);
				if (windResponse.ok) {
					const noaaWindData = await windResponse.json();
					console.log("✅ NOAA wind data received:", noaaWindData);
					setWindData(noaaWindData);

					// Process NOAA data into wind vectors for visualization
					processWindVectors(noaaWindData, north, south, east, west);
				} else {
					console.warn("⚠️ NOAA wind data failed, using demo data");
					// Fallback to demo wind grid
					const demoWindResponse = await fetch(
						`${apiBaseUrl}/api/wind-grid-demo?north=${north}&south=${south}&east=${east}&west=${west}`
					);
					if (demoWindResponse.ok) {
						const demoWindData = await demoWindResponse.json();
						console.log("🌬️ Demo wind data:", demoWindData);
						setWindVectors(
							demoWindData.data.map((point: any) => ({
								...point,
								source: "demo" as const,
							}))
						);
					} else {
						// Create some basic demo data if even the demo endpoint fails
						console.log("🔧 Creating fallback wind data");
						const fallbackVectors = [];
						for (let i = 0; i < 5; i++) {
							for (let j = 0; j < 5; j++) {
								fallbackVectors.push({
									lat: 40.6 + i * 0.05,
									lon: -74.1 + j * 0.05,
									u: Math.random() * 4 - 2,
									v: Math.random() * 4 - 2,
									speed: Math.random() * 8 + 2,
									direction: Math.random() * 360,
									source: "demo" as const,
								});
							}
						}
						console.log(
							`🔧 Created ${fallbackVectors.length} fallback vectors`
						);
						setWindVectors(fallbackVectors);
					}
				}
			} catch (error) {
				console.error("Error fetching data:", error);
			}
		};

		fetchData();
	}, []);

	// Monitor wind vectors changes
	useEffect(() => {
		console.log(`🔄 Wind vectors updated: ${windVectors.length} vectors`);
		if (windVectors.length > 0) {
			console.log("Wind vectors available for rendering");
		}
	}, [windVectors]);

	// Function to process NOAA wind data into visualization vectors
	const processWindVectors = (
		noaaData: NOAAWindData,
		north: number,
		south: number,
		east: number,
		west: number
	) => {
		if (!noaaData.current) return;

		const current = noaaData.current;
		const vectors: WindVector[] = [];

		// Create a grid of wind vectors around NYC using current NOAA conditions
		// 12x12 grid for good coverage without overwhelming the map
		const latStep = (north - south) / 11;
		const lonStep = (east - west) / 11;

		for (let i = 0; i < 12; i++) {
			for (let j = 0; j < 12; j++) {
				const lat = south + i * latStep;
				const lon = west + j * lonStep;

				// Use real NOAA wind components with slight spatial variation
				const baseU = current.u_component;
				const baseV = current.v_component;

				// Add small random variation for realistic spatial wind pattern
				const spatialVariation = 0.2; // ±20% variation
				const u =
					baseU * (1 + (Math.random() - 0.5) * spatialVariation);
				const v =
					baseV * (1 + (Math.random() - 0.5) * spatialVariation);

				const speed = Math.sqrt(u * u + v * v);
				const direction =
					((Math.atan2(u, v) * 180) / Math.PI + 360) % 360;

				vectors.push({
					lat: parseFloat(lat.toFixed(4)),
					lon: parseFloat(lon.toFixed(4)),
					u: parseFloat(u.toFixed(2)),
					v: parseFloat(v.toFixed(2)),
					speed: parseFloat(speed.toFixed(2)),
					direction: parseFloat(direction.toFixed(1)),
					source: "noaa",
				});
			}
		}

		console.log(
			`🌪️ Generated ${vectors.length} wind vectors from NOAA data`
		);
		console.log("Sample wind vector:", vectors[0]);
		setWindVectors(vectors);
	};

	// Function to create wind arrow icon
	const createWindArrow = (
		speed: number,
		direction: number,
		source: "noaa" | "demo"
	) => {
		try {
			// Determine arrow size and color based on wind speed
			let color = "#64748B"; // Default gray
			let size = 16;
			let opacity = 0.8;

			if (speed < 2) {
				color = "#06B6D4"; // Cyan for very light wind
				size = 14;
				opacity = 0.6;
			} else if (speed < 5) {
				color = "#3B82F6"; // Blue for light wind
				size = 18;
				opacity = 0.7;
			} else if (speed < 10) {
				color = "#10B981"; // Green for moderate wind
				size = 22;
				opacity = 0.8;
			} else if (speed < 15) {
				color = "#F59E0B"; // Amber for strong wind
				size = 26;
				opacity = 0.9;
			} else {
				color = "#EF4444"; // Red for very strong wind
				size = 30;
				opacity = 1.0;
			}

			// Add special styling for NOAA vs demo data
			if (source === "noaa") {
				// NOAA data gets a subtle border to indicate real data
				color = color; // Keep same colors but add border in CSS
			}

			const arrowHtml = `
			<div class="wind-arrow-container" style="
				width: ${size}px;
				height: ${size}px;
				display: flex;
				align-items: center;
				justify-content: center;
				transform: rotate(${direction}deg);
				opacity: ${opacity};
			">
				<svg width="${size}" height="${size}" viewBox="0 0 24 24" style="${
				source === "noaa"
					? "filter: drop-shadow(0 0 2px rgba(0,0,0,0.3));"
					: ""
			}">
					<path d="M12 2 L20 20 L12 16 L4 20 Z" fill="${color}" stroke="${
				source === "noaa" ? "#ffffff" : "none"
			}" stroke-width="${source === "noaa" ? "0.5" : "0"}"/>
				</svg>
			</div>
		`;

			return L.divIcon({
				html: arrowHtml,
				className: `wind-arrow ${
					source === "noaa" ? "noaa-wind" : "demo-wind"
				}`,
				iconSize: [size, size],
				iconAnchor: [size / 2, size / 2],
				popupAnchor: [0, -size / 2],
			});
		} catch (error) {
			console.error("Error creating wind arrow:", error);
			// Return a simple default icon if there's an error
			return L.divIcon({
				html: `<div style="width: 16px; height: 16px; background: #3B82F6; border-radius: 50%;"></div>`,
				className: "wind-error-fallback",
				iconSize: [16, 16],
				iconAnchor: [8, 8],
			});
		}
	};

	// Helper function to convert cardinal direction to readable format
	const getWindDirectionText = (degrees: number): string => {
		const directions = [
			"N",
			"NNE",
			"NE",
			"ENE",
			"E",
			"ESE",
			"SE",
			"SSE",
			"S",
			"SSW",
			"SW",
			"WSW",
			"W",
			"WNW",
			"NW",
			"NNW",
		];
		const index = Math.round(degrees / 22.5) % 16;
		return directions[index];
	};

	return (
		<div style={{ height: "100%", width: "100%", position: "relative" }}>
			{/* Add CSS styles for wind arrows */}
			<style jsx>{`
				.wind-arrow {
					transition: all 0.2s ease;
				}
				.wind-arrow:hover {
					transform: scale(1.1) !important;
					z-index: 1000;
				}
				.noaa-wind .wind-arrow-container {
					filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.3));
				}
				.demo-wind .wind-arrow-container {
					opacity: 0.8;
				}

				/* Responsive styles */
				@media (max-width: 768px) {
					.info-panel-toggle-btn {
						right: 15px !important;
					}
				}

				@media (max-width: 480px) {
					.info-panel-toggle-btn {
						width: 40px !important;
						height: 40px !important;
						font-size: 16px !important;
						top: 10px !important;
						right: 10px !important;
					}
				}
			`}</style>

			{/* Heatmap Toggle Button */}
			<button
				className="heatmap-toggle-btn"
				onClick={() => setShowHeatmap(!showHeatmap)}
				style={{
					position: "absolute",
					top: "20px",
					right: "20px",
					backgroundColor: showHeatmap ? "#10B981" : "#3B82F6",
					color: "white",
					border: "none",
					borderRadius: "8px",
					padding: "12px 20px",
					cursor: "pointer",
					boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
					zIndex: 1002,
					fontSize: "14px",
					fontWeight: "bold",
					transition: "all 0.3s ease",
				}}
				onMouseOver={(e) => {
					e.currentTarget.style.opacity = "0.9";
				}}
				onMouseOut={(e) => {
					e.currentTarget.style.opacity = "1";
				}}>
				{showHeatmap ? "🔵 Show Point Grid" : "🔥 Show Heat Map"}
			</button>

			<MapContainer
				center={position}
				zoom={zoom}
				zoomControl={true}
				style={{ height: "100%", width: "100%" }}>
				<TileLayer
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
				/>				<LayersControl position="topright">
					{/* TEMPO Satellite Data Layer - Point Grid */}
					{!showHeatmap && (
						<LayersControl.Overlay
							name="TEMPO NO₂ Data"
							checked>
							<Pane
								name="satellitePane"
								style={{ zIndex: 200 }}>
								{tempoData && (
									<CircleMarker
										center={[
											tempoData.location.y,
											tempoData.location.x,
										]}
										radius={20}
										fillColor="#ff3300"
										fillOpacity={0.6}
										color="#ff0000"
										weight={1}>
										<Popup>
											<div>
												<h3>TEMPO NO₂ Measurement</h3>
												<p>
													Value:{" "}
													{Number(
														tempoData.value
													).toExponential(2)}{" "}
													molecules/cm²
												</p>
												<p>
													Location: (
													{tempoData.location.y.toFixed(
														3
													)}
													°,{" "}
													{tempoData.location.x.toFixed(
														3
													)}
													°)
												</p>
											</div>
										</Popup>
									</CircleMarker>
								)}
							</Pane>
						</LayersControl.Overlay>
					)}

					{/* Surface Pressure Data Layer */}
					{surfacePressureData && (
						<LayersControl.Overlay
							name="🌡️ Surface Pressure (NOAA)"
							checked>
							<Pane
								name="pressurePane"
								style={{ zIndex: 190 }}>
								<CircleMarker
									center={[
										surfacePressureData.location.lat,
										surfacePressureData.location.lon,
									]}
									radius={15}
									fillColor="#1E90FF"
									fillOpacity={0.7}
									color="#0066CC"
									weight={2}>
									<Popup>
										<div style={{ minWidth: "220px" }}>
											<h4 
												style={{
													margin: "0 0 8px 0",
													fontSize: "16px",
													fontWeight: "bold",
													color: "#1F2937",
												}}>
												🌡️ NOAA Surface Pressure
											</h4>
											<div 
												style={{
													padding: "8px 0",
													borderTop: "1px solid #E5E7EB",
													borderBottom: "1px solid #E5E7EB",
													margin: "8px 0",
												}}>
												<p style={{
													margin: "4px 0",
													fontSize: "18px",
													fontWeight: "bold",
													color: "#0066CC",
												}}>
													{surfacePressureData.current.pressure_hpa.toFixed(1)} hPa
												</p>
												<p style={{
													margin: "4px 0",
													fontSize: "13px",
													color: "#374151",
												}}>
													<strong>Pressure:</strong> {surfacePressureData.current.pressure_inhg.toFixed(2)} inHg
												</p>
												<p style={{
													margin: "4px 0",
													fontSize: "13px",
													color: "#374151",
												}}>
													<strong>Station:</strong> {surfacePressureData.current.station}
												</p>
												<p style={{
													margin: "4px 0",
													fontSize: "13px",
													color: "#374151",
												}}>
													<strong>Quality:</strong> {surfacePressureData.current.quality === 'V' ? 'Valid' : surfacePressureData.current.quality}
												</p>
												<p style={{
													margin: "4px 0",
													fontSize: "12px",
													color: "#6B7280",
												}}>
													<strong>Timestamp:</strong><br/>
													{new Date(surfacePressureData.current.timestamp).toLocaleString()}
												</p>
											</div>
											<div style={{
												fontSize: "11px",
												color: "#6B7280",
												marginTop: "6px",
											}}>
												<strong>Location:</strong> NYC ({surfacePressureData.location.lat.toFixed(3)}°, {surfacePressureData.location.lon.toFixed(3)}°)
												<br/>
												<strong>Data Source:</strong> NOAA Weather Station
											</div>
										</div>
									</Popup>
								</CircleMarker>
							</Pane>
						</LayersControl.Overlay>
					)}

					{/* NOAA GFS Wind Layer - Always Visible */}
					{windVectors.length > 0 && (
						<Pane
							name="windPane"
							style={{ zIndex: 150 }}>
							{windVectors.map((wind, index) => (
								<Marker
									key={`wind-${index}`}
									position={[wind.lat, wind.lon]}
									icon={createWindArrow(
										wind.speed,
										wind.direction,
										wind.source
									)}>
									<Popup>
										<div style={{ minWidth: "200px" }}>
											<h4
												style={{
													margin: "0 0 8px 0",
													fontSize: "16px",
													fontWeight: "bold",
													color: "#1F2937",
												}}>
												{wind.source === "noaa"
													? "🌪️ NOAA GFS Wind Data"
													: "🌬️ Demo Wind Data"}
											</h4>
											<div
												style={{
													padding: "8px 0",
													borderTop:
														"1px solid #E5E7EB",
													borderBottom:
														"1px solid #E5E7EB",
													margin: "8px 0",
												}}>
												<p
													style={{
														margin: "4px 0",
														fontSize: "13px",
														color: "#374151",
													}}>
													<strong>Speed:</strong>{" "}
													{wind.speed.toFixed(1)} m/s
													(
													{(
														wind.speed * 2.237
													).toFixed(1)}{" "}
													mph)
												</p>
												<p
													style={{
														margin: "4px 0",
														fontSize: "13px",
														color: "#374151",
													}}>
													<strong>Direction:</strong>{" "}
													{wind.direction.toFixed(0)}°
													(
													{getWindDirectionText(
														wind.direction
													)}
													)
												</p>
												<p
													style={{
														margin: "4px 0",
														fontSize: "13px",
														color: "#374151",
													}}>
													<strong>Components:</strong>{" "}
													U: {wind.u.toFixed(1)} m/s,
													V: {wind.v.toFixed(1)} m/s
												</p>
												{wind.source === "noaa" &&
													windData?.current && (
														<>
															<p
																style={{
																	margin: "4px 0",
																	fontSize:
																		"12px",
																	color: "#6B7280",
																}}>
																<strong>
																	Temperature:
																</strong>{" "}
																{
																	windData
																		.current
																		.temperature
																}
																°
																{
																	windData
																		.current
																		.temperature_unit
																}
															</p>
															<p
																style={{
																	margin: "4px 0",
																	fontSize:
																		"12px",
																	color: "#6B7280",
																}}>
																<strong>
																	Humidity:
																</strong>{" "}
																{
																	windData
																		.current
																		.humidity
																}
																%
															</p>
														</>
													)}
												<div
													style={{
														marginTop: "8px",
														fontSize: "11px",
														color: "#9CA3AF",
													}}>
													<strong>Source:</strong>{" "}
													{wind.source === "noaa"
														? "NOAA Global Forecast System"
														: "Simulated Pattern"}
													{wind.source === "noaa" &&
														windData?.meta && (
															<>
																<br />
																Grid:{" "}
																{
																	windData
																		.meta
																		.location
																		.grid_id
																}{" "}
																(
																{
																	windData
																		.meta
																		.location
																		.grid_x
																}
																,{" "}
																{
																	windData
																		.meta
																		.location
																		.grid_y
																}
																)
															</>
														)}
												</div>
											</div>
										</div>
									</Popup>
								</Marker>
							))}
						</Pane>
					)}
				</LayersControl>

				{/* TEMPO Heat Map Layer */}
				{showHeatmap && heatmapData.length > 0 && (
					<HeatmapLayer
						points={heatmapData}
						longitudeExtractor={(point: [number, number, number]) =>
							point[1]
						}
						latitudeExtractor={(point: [number, number, number]) =>
							point[0]
						}
						intensityExtractor={(point: [number, number, number]) =>
							point[2]
						}
						max={1.0}
						radius={25}
						blur={15}
					/>
				)}

				{/* Map over stations and render markers with custom icons */}
				{stations.map((station) => {
					// Check if station is active (data from last 30 days)
					const lastUpdate = new Date(station.datetimeLast.utc);
					const thirtyDaysAgo = new Date();
					thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
					const isActive = lastUpdate > thirtyDaysAgo;

					// Get parameter name for icon customization
					const parameterName =
						station.sensors && station.sensors.length > 0
							? station.sensors[0].parameter.name
							: "unknown";

					return (
						<Marker
							key={station.id}
							position={[
								station.coordinates.latitude,
								station.coordinates.longitude,
							]}
							icon={createCustomIcon(parameterName, isActive)}>
							<Popup>
								<div style={{ minWidth: "200px" }}>
									<h3
										style={{
											margin: "0 0 8px 0",
											fontSize: "18px",
											fontWeight: "bold",
											color: "#1F2937",
										}}>
										{station.name}
									</h3>
									<div
										style={{
											padding: "8px 0",
											borderTop: "1px solid #E5E7EB",
											borderBottom: "1px solid #E5E7EB",
											margin: "8px 0",
										}}>
										<p
											style={{
												margin: "4px 0",
												fontSize: "14px",
												color: "#4B5563",
											}}>
											📍 <strong>Distance:</strong>{" "}
											{(station.distance / 1000).toFixed(
												2
											)}{" "}
											km away
										</p>
										{station.sensors &&
											station.sensors.length > 0 && (
												<p
													style={{
														margin: "4px 0",
														fontSize: "14px",
														color: "#4B5563",
													}}>
													🔬{" "}
													<strong>Measuring:</strong>{" "}
													{
														station.sensors[0]
															.parameter
															.displayName
													}{" "}
													(
													{
														station.sensors[0]
															.parameter.units
													}
													)
												</p>
											)}
									</div>
									<p
										style={{
											margin: "4px 0",
											fontSize: "12px",
											color: isActive
												? "#10B981"
												: "#EF4444",
											fontWeight: "bold",
										}}>
										{isActive ? "🟢 Active" : "🔴 Inactive"}
									</p>
									<p
										style={{
											margin: "4px 0",
											fontSize: "12px",
											color: "#9CA3AF",
										}}>
										Last update:{" "}
										{lastUpdate.toLocaleDateString()} at{" "}
										{lastUpdate.toLocaleTimeString()}
									</p>
								</div>
							</Popup>
						</Marker>
					);
				})}
			</MapContainer>
		</div>
	);
}
