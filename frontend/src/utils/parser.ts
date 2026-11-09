import {
  ParsedFlightInfo,
  ParsedHotelItem,
  ParsedItineraryDay,
  ParsedTripPlan,
  ParsedWeatherInfo,
  TravelSuccessResponse,
} from '../types';

export function parseTripResponse(
  query: string,
  data: TravelSuccessResponse
): ParsedTripPlan {
  // 1. Destination Title
  const destMatch =
    query.match(/trip to ([\w\s,&]+?)(?: in| for| with|$)/i) ||
    query.match(/visit ([\w\s,&]+?)(?: in| for| with|$)/i) ||
    query.match(/to ([\w\s,&]+?)(?: in| for| with|$)/i);

  const destinationTitle = destMatch
    ? destMatch[1].trim()
    : query.split(',')[0].replace(/plan a|trip to/gi, '').trim() || 'Custom Itinerary';

  // 2. Duration
  const daysMatch =
    query.match(/(\d+)[ -]day/i) ||
    data.itinerary.match(/Day (\d+)/gi);

  const durationLabel = daysMatch
    ? typeof daysMatch[1] === 'string'
      ? `${daysMatch[1]} Days`
      : `${daysMatch.length} Days`
    : 'Multi-Day Journey';

  // 3. Estimated Budget from answer or itinerary
  const budgetMatch =
    data.answer.match(/(?:Estimated Budget|Budget Range|Total Budget)[:\s*]+([^\n\r]+)/i) ||
    data.answer.match(/(\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per person|total))?)/i);

  const estimatedBudget = budgetMatch ? budgetMatch[1].replace(/[*#]/g, '').trim() : undefined;

  // 4. Parse Flight Info
  const flights = parseFlights(data.flight_results);

  // 5. Parse Hotels
  const hotels = parseHotels(data.hotel_results);

  // 6. Parse Itinerary Days
  const itineraryDays = parseItineraryDays(data.itinerary);

  // 7. Parse Weather & Packing
  const weather = parseWeather(data.weather_results);

  // 8. Overview Summary
  const overviewSummary = cleanOverview(data.answer);

  // 9. Recommendations
  const recommendations = extractRecommendations(data.answer);

  return {
    destinationTitle: capitalizeTitle(destinationTitle),
    durationLabel,
    estimatedBudget,
    overviewSummary,
    flights,
    hotels,
    itineraryDays,
    weather,
    recommendations,
  };
}

function parseFlights(raw: string): ParsedFlightInfo {
  if (!raw) return { rawText: '' };

  const durationMatch =
    raw.match(/(?:flight duration|duration|flight time)[:\s*]+([^\n\r.]+)/i) ||
    raw.match(/(\d+(?:-\d+)?\s*(?:hours|hrs))/i);

  const fareMatch =
    raw.match(/(?:estimated airfare|airfare range|fare range|estimated fare|price)[:\s*]+([^\n\r.]+)/i) ||
    raw.match(/(\$[\d,]+(?:\s*-\s*\$[\d,]+)?)/i);

  // Extract airlines
  const airlinesMatch = raw.match(/(?:airlines|major airlines|carriers)[:\s*]+([^\n\r]+)/i);
  let airlines: string[] = [];
  if (airlinesMatch) {
    airlines = airlinesMatch[1]
      .split(/[,;|•]/)
      .map(a => a.replace(/[*_]/g, '').trim())
      .filter(a => a.length > 2 && a.length < 35);
  }

  // Extract airports
  const airportsMatch = raw.match(/(?:airports|departure & arrival airports|airports serving)[:\s*]+([^\n\r]+)/i);
  let airports: string[] = [];
  if (airportsMatch) {
    airports = airportsMatch[1]
      .split(/[,;|•]/)
      .map(a => a.replace(/[*_]/g, '').trim())
      .filter(a => a.length > 2 && a.length < 40);
  }

  // Season tips
  const seasonMatch = raw.match(/(?:peak season|best time to fly|booking advice)[:\s*]+([^\n\r]+)/i);

  return {
    duration: durationMatch ? durationMatch[1].replace(/[*_]/g, '').trim() : undefined,
    fareRange: fareMatch ? fareMatch[1].replace(/[*_]/g, '').trim() : undefined,
    airlines: airlines.length > 0 ? airlines.slice(0, 5) : undefined,
    airports: airports.length > 0 ? airports.slice(0, 4) : undefined,
    seasonTips: seasonMatch ? seasonMatch[1].replace(/[*_]/g, '').trim() : undefined,
    rawText: raw,
  };
}

function parseHotels(raw: string): ParsedHotelItem[] {
  if (!raw) return [];

  const items: ParsedHotelItem[] = [];
  // Split by hotel numbered headers or bullet points
  const blocks = raw.split(/(?=\d+\.\s+\*\*|###\s+|(?:\*\*Hotel|\*\*Option)\s+\d+)/i);

  blocks.forEach((block, idx) => {
    const trimmed = block.trim();
    if (!trimmed || trimmed.length < 20) return;

    const nameMatch = trimmed.match(/(?:\d+\.\s*)?\*\*([^*]+)\*\*/);
    const name = nameMatch ? nameMatch[1].replace(/^Hotel:?/i, '').trim() : `Curated Accommodation #${idx + 1}`;

    // Detect tier
    let tier: ParsedHotelItem['tier'] = 'General';
    const lower = trimmed.toLowerCase();
    if (lower.includes('luxury') || lower.includes('5-star') || lower.includes('premium')) {
      tier = 'Luxury';
    } else if (lower.includes('boutique') || lower.includes('mid-range') || lower.includes('charming')) {
      tier = 'Boutique';
    } else if (lower.includes('budget') || lower.includes('hostel') || lower.includes('affordable')) {
      tier = 'Value';
    }

    // Rate match
    const rateMatch = trimmed.match(/(?:rate|price|nightly|cost)[:\s*]+([^\n\r,]+)/i) ||
      trimmed.match(/(\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*\/night)?)/i);

    // Location match
    const locMatch = trimmed.match(/(?:location|neighborhood|area)[:\s*]+([^\n\r.]+)/i);

    // Amenities
    const amenitiesMatch = trimmed.match(/(?:amenities|features|highlights)[:\s*]+([^\n\r]+)/i);
    let amenities: string[] = [];
    if (amenitiesMatch) {
      amenities = amenitiesMatch[1]
        .split(/[,;|•]/)
        .map(a => a.replace(/[*_]/g, '').trim())
        .filter(a => a.length > 2 && a.length < 30);
    }

    items.push({
      name,
      tier,
      priceRange: rateMatch ? rateMatch[1].replace(/[*_]/g, '').trim() : undefined,
      location: locMatch ? locMatch[1].replace(/[*_]/g, '').trim() : undefined,
      amenities: amenities.length > 0 ? amenities.slice(0, 4) : undefined,
      description: trimmed,
    });
  });

  return items;
}

function parseItineraryDays(raw: string): ParsedItineraryDay[] {
  if (!raw) return [];

  const days: ParsedItineraryDay[] = [];
  // Split on Day 1, Day 2 headers
  const dayBlocks = raw.split(/(?=(?:###\s+|##\s+|\*\*|\b)Day\s+\d+[:\s-])/i);

  dayBlocks.forEach(block => {
    const trimmed = block.trim();
    if (!trimmed) return;

    const dayMatch = trimmed.match(/Day\s+(\d+)[:\s-]*(.*?)(?:\n|$)/i);
    if (!dayMatch) return;

    const dayNumber = parseInt(dayMatch[1], 10);
    const title = dayMatch[2].replace(/[*_#]/g, '').trim() || `Day ${dayNumber} Exploration`;

    // Extract segments
    const morningMatch = trimmed.match(/(?:Morning|Morning Activity|AM)[:\s*]+([^\n\r]+(?:\n[^\n\r#*-]+)?)/i);
    const afternoonMatch = trimmed.match(/(?:Afternoon|Afternoon Activity|PM)[:\s*]+([^\n\r]+(?:\n[^\n\r#*-]+)?)/i);
    const eveningMatch = trimmed.match(/(?:Evening|Night|Dinner)[:\s*]+([^\n\r]+(?:\n[^\n\r#*-]+)?)/i);

    // Extract bullet points as highlights
    const highlights = trimmed
      .split('\n')
      .filter(l => l.trim().startsWith('- ') || l.trim().startsWith('* '))
      .map(l => l.replace(/^[-*]\s*/, '').replace(/[*_]/g, '').trim())
      .filter(l => l.length > 10)
      .slice(0, 4);

    days.push({
      dayNumber,
      title,
      morning: morningMatch ? morningMatch[1].replace(/[*_]/g, '').trim() : undefined,
      afternoon: afternoonMatch ? afternoonMatch[1].replace(/[*_]/g, '').trim() : undefined,
      evening: eveningMatch ? eveningMatch[1].replace(/[*_]/g, '').trim() : undefined,
      highlights: highlights.length > 0 ? highlights : undefined,
      rawText: trimmed,
    });
  });

  return days;
}

function parseWeather(raw: string): ParsedWeatherInfo {
  if (!raw) {
    return {
      packingList: ['Comfortable walking footwear', 'Universal power adapter', 'Weather-appropriate layers'],
      rawText: '',
    };
  }

  // Current conditions
  const currentMatch = raw.match(/(?:current weather|conditions|temperature)[:\s*]+([^\n\r]+)/i);

  // Temp range
  const tempMatch = raw.match(/(\d+°(?:C|F)(?:\s*(?:to|-)\s*\d+°(?:C|F))?)/i);

  // Forecast
  const forecastMatch = raw.match(/(?:forecast|outlook|expect)[:\s*]+([^\n\r]+)/i);

  // Packing items
  const packingMatch = raw.match(/(?:packing|what to pack|bring|essentials)[:\s*]+([\s\S]+?)(?:\n\n|\n[#A-Z]|$)/i);
  let packingList: string[] = [];

  if (packingMatch) {
    packingList = packingMatch[1]
      .split('\n')
      .map(line => line.replace(/^[-*•\d.]+\s*/, '').replace(/[*_]/g, '').trim())
      .filter(line => line.length > 3 && line.length < 60);
  }

  if (packingList.length === 0) {
    packingList = [
      'Comfortable walking shoes',
      'Light rain jacket or compact umbrella',
      'Portable power bank & universal adapter',
      'Smart casual evening wear',
      'Daypack for sightseeing essentials',
    ];
  }

  return {
    currentConditions: currentMatch ? currentMatch[1].replace(/[*_]/g, '').trim() : undefined,
    temperature: tempMatch ? tempMatch[1] : undefined,
    forecastSummary: forecastMatch ? forecastMatch[1].replace(/[*_]/g, '').trim() : undefined,
    packingList: packingList.slice(0, 6),
    rawText: raw,
  };
}

function cleanOverview(answer: string): string {
  if (!answer) return 'Custom travel blueprint generated for your journey.';
  // Pull the trip summary section or first 2 paragraphs
  const summaryMatch = answer.match(/(?:Trip Summary|Overview)[:\s*]+([\s\S]+?)(?:\n##|\n\d+\.|$)/i);
  if (summaryMatch) {
    return summaryMatch[1].replace(/[*_#]/g, '').trim();
  }

  const paragraphs = answer.split('\n\n').filter(p => !p.trim().startsWith('#') && p.length > 40);
  return paragraphs[0] ? paragraphs[0].replace(/[*_#]/g, '').trim() : answer.slice(0, 240);
}

function extractRecommendations(answer: string): string[] {
  if (!answer) return [];
  const recMatch = answer.match(/(?:Final Recommendations|Tips|Advice)[:\s*]+([\s\S]+?)$/i);
  if (!recMatch) return [];

  return recMatch[1]
    .split('\n')
    .map(line => line.replace(/^[-*•\d.]+\s*/, '').replace(/[*_]/g, '').trim())
    .filter(line => line.length > 10 && line.length < 140)
    .slice(0, 4);
}

function capitalizeTitle(str: string): string {
  return str
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}
