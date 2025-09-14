namespace CalendarService.DotNet.Services;
using CalendarService.DotNet.Models;
using Microsoft.Graph.Models;

public interface IOutlookCalendarService
{
    Task<Event> CreateEventAsync(string userPrincipalName, EventInput eventInput);
}