using CalendarService.DotNet.Models;
using Microsoft.Graph;
using Microsoft.Graph.Models;
using System.Globalization;

namespace CalendarService.DotNet.Services;

public class OutlookCalendarService : IOutlookCalendarService
{
    private readonly GraphServiceClient _graphServiceClient;

    public OutlookCalendarService(GraphServiceClient graphServiceClient)
    {
        _graphServiceClient = graphServiceClient;
    }

    public async Task<Event> CreateEventAsync(string userPrincipalName, EventInput eventInput)
    {
        var format = "dd/MM/yyyy HH:mm";
        var dateTimeString = $"{eventInput.Data} {eventInput.Hora}";
        if (!DateTime.TryParseExact(dateTimeString, format, CultureInfo.InvariantCulture, DateTimeStyles.None, out var startDateTime))
        {
            throw new ArgumentException("Formato de data ou hora inválido.");
        }

        var endDateTime = startDateTime.AddHours(1);

        var graphEvent = new Event
        {
            Subject = eventInput.Titulo,
            Body = new ItemBody
            {
                ContentType = BodyType.Text,
                Content = eventInput.Description
            },
            Start = new DateTimeTimeZone
            {
                DateTime = endDateTime.ToString("o"),
                TimeZone = "E. South America Standard Time"
            },
            End = new DateTimeTimeZone
            {
                DateTime = endDateTime.ToString("o"),
                TimeZone = "E. South America Standard Time"
            }
        };

        return await _graphServiceClient.Users[userPrincipalName].Calendars["Calendar"].Events
            .PostAsync(graphEvent);
    }
}