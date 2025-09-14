using System.ComponentModel.DataAnnotations;

namespace CalendarService.DotNet.Models;

public class EventInput
{
    [Required]
    public string? ChatId { get; set; }

    [Required]
    public string? Titulo { get; set; }

    [Required]
    public string? Description { get; set; }

    [Required]
    public string? Data { get; set; } 

    [Required]
    public string? Hora { get; set; }
}